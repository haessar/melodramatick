from dal_select2.widgets import ModelSelect2
import django_filters

EMPTY_LABEL_PATTERN = "--{}--"


class CustomEmptyLabelMixin:
    @classmethod
    def get_filters(cls):
        filters = super().get_filters()
        for label, filter in filters.items():
            if isinstance(filter, django_filters.ChoiceFilter):
                empty_label = EMPTY_LABEL_PATTERN.format(filter.label if filter.label else label.title())
                if "widget" in filter.extra and isinstance(filter.extra["widget"], ModelSelect2):
                    filter.extra["widget"].attrs["data-placeholder"] = empty_label
                filter.extra["empty_label"] = empty_label
        return filters
