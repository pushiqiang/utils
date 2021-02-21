from django.db import models


class Model(models.Model):
    """对象字段值变化差异更新 BaseModel"""
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_data = {}
        for field in iter(self._meta.fields):
            self._init_data[field.attname] = getattr(self, field.attname, None)

    def _get_changed_fields(self):
        _changed_field = [field.attname for field in iter(self._meta.fields)
                          if getattr(self, field.attname, None) != self._init_data.get(field.attname)]
        return _changed_field or None

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        update_fields = update_fields or self._get_changed_fields()
        super().save(force_insert, force_update, using, update_fields)
