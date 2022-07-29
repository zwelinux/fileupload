from django.contrib import admin
from .models import Idea
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Group
from django import forms
from django.utils.html import format_html

admin.site.index_title = 'Idea Creation Team'
admin.site.site_header = 'Idea Creation Team'
admin.site.site_title = 'Admin Panel'

class IdeaAdminForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = "__all__"

    share_to_gp = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Share To Group',
            is_stacked=False
        )
    )

    def init(self, *args, **kwargs):
        super(IdeaAdminForm, self).init(*args, **kwargs)
        if self.instance.pk:
            self.fields['share_to_gp'].initial = self.instance.share_to_gp.all()

    def save(self, commit=True):
        idea = super(IdeaAdminForm, self).save(commit=False)  
        if commit:
            idea.save()

        if idea.pk:
            idea.share_to_gp_set = self.cleaned_data['share_to_gp']
            self.save_m2m()

        return idea

class IdeaAdmin(admin.ModelAdmin):
    form = IdeaAdminForm
    list_display = ["title", "powerpoint", "note", "uploaded_by"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["queryset"] = get_user_model().objects.filter(
                username=request.user.username
            )
        return super(IdeaAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.readonly_fields + ("uploaded_by",)
        return self.readonly_fields

    def add_view(self, request, form_url="", extra_context=None):
        data = request.GET.copy()
        data["uploaded_by"] = request.user
        request.GET = data
        return super(IdeaAdmin, self).add_view(
            request, form_url="", extra_context=extra_context
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs 
        elif request.user.groups.exists():
            user_groups = request.user.groups.all()
            user_groups = list(user_groups)
            user_groups = user_groups
            return qs.filter(share_to_gp__in=user_groups)
        else:
            return qs.filter(uploaded_by=request.user)
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.uploaded_by != request.user:
            return ["title", "share_to_gp", "powerpoint", "note", "uploaded_by"]
        else:
            return []

    def has_delete_permission(self, request, obj=None):
        if obj and obj.uploaded_by != request.user:
            return False
        return True

admin.site.register(Idea, IdeaAdmin)
