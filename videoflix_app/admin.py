from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Video

class VideoResource(resources.ModelResource):

    class Meta:
        model = Video
        
@admin.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    pass  



from .admin import VideoResource
dataset = VideoResource().export()
print(dataset.csv)
# id,name,author,author_email,imported,published,price,categories
# 2,Some book,1,,0,2012-12-05,8.85,1