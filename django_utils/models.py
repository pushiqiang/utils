import time
from django.db import models


class Model(models.Model):
    """
    1. 对象字段值变化差异更新 BaseModel（不包含外键对象）
    2. 版本号version控制实现乐观锁（version字段类型只允许整型或时间戳类型）
    """
    VERSION_FIELD_NAME = 'version'

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_data = {}
        self._version = getattr(self, self.VERSION_FIELD_NAME, None)
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

    def _prepare_optimistic_lock(self, qs, values):
        if self._version:
            qs = qs.filter(**{self.VERSION_FIELD_NAME: self._version})
            version_field = self._meta.get_field(self.VERSION_FIELD_NAME)
            # int
            if isinstance(self._version, int):
                values.append((version_field, None, self._version + 1))
            # timestamp: float
            elif isinstance(self._version, float):
                values.append((version_field, None, time))
            else:
                raise ValueError('Optimistic locking version field type must be `integer` or `float`')

        return qs, values

    def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
        base_qs, values = self._prepare_optimistic_lock(base_qs, values)
        return super()._do_update(base_qs, using, pk_val, values, update_fields, forced_update)
