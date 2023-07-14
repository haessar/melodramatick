from django.contrib import admin

from .models import Company, Performance, Venue

admin.site.register(Company)
admin.site.register(Venue)


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ("get_works", "get_composers", "company", "venue", "date")
    list_filter = (('user', admin.RelatedOnlyFieldListFilter),)
    actions = ['merge_performances', 'split_performance']
    ordering = ['-date', ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def get_works(self, obj):
        return ", ".join([w.title for w in obj.work.all()])
    get_works.short_description = "Work(s)"

    def get_composers(self, obj):
        return ", ".join(set(w.composer.surname for w in obj.work.all()))
    get_composers.short_description = 'Composer(s)'

    @admin.action(description='Merge selected performances')
    def merge_performances(self, request, queryset):
        works = []
        p = Performance.objects.create(user=request.user)
        for performance in queryset:
            works.extend(performance.work.all())
            performance.delete()
        p.work.add(*set(works))
        self.message_user(request, "Your performances have been merged.")

    @admin.action(description='Split selected performance')
    def split_performance(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Can not split more than one selected performances.")
            return
        performance = queryset.get()
        works = performance.work.all()
        if works.count() < 2:
            self.message_user(request, "Can not split performance of single work.")
            return
        for work in works:
            p = Performance.objects.create(user=request.user)
            p.work.add(work)
        performance.delete()
        self.message_user(request, "Your performance has been split.")

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)
