from django.db import models

class WorkSchedule(models.Model):
    title = models.CharField(max_length=200, verbose_name="รายละเอียดงาน")
    start_date = models.DateField(verbose_name="วันที่")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.start_date})"