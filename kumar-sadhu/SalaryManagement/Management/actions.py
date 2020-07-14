import csv
from django.http import HttpResponse

def export_as_csv_action(description="Export selected objects as CSV file", fields=None, exclude=None, header=True):

    def export_as_csv(modeladmin, request, queryset):

        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])

        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset

        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % str(opts).replace('.', '_')

        writer = csv.writer(response)

        if header:
            writer.writerow(list(field_names))
        for obj in queryset:
            row = [getattr(obj, field)() if callable(getattr(obj, field)) else getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response

    export_as_csv.short_description = description
    return export_as_csv
