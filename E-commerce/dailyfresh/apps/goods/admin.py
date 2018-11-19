from django.contrib import admin
from django.core.cache import cache  #导入页面数据缓存数据包
from goods.models import GoodsType,Goods,GoodsImage,GoodsSKU,IndexGoodsBanner,IndexTypeGoodsBanner,IndexPromotionBanner

class BaseModelAdmin(admin.ModelAdmin):
     def save_model(self, request, obj, form, change):
        """  后台新增或更新表中的数据时调用这个方法"""
        super().save_model(request,obj,form,change)
        #发出任务，让celery worker重新生成静态页面
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        #清除首页的缓存数据,每当后台变动，就删除页面缓存，等打开页面重新存入缓存即可
        cache.delete("index_page_data")

     def delete_model(self, request, obj):
        """  删除表中的数据时也使用"""
        super().save_model(request, obj)
        # 发出任务，让celery worker重新生成静态页面
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页的缓存数据
        cache.delete("index_page_data")

class GoodsTypeAdmin(BaseModelAdmin):
    list_display = ["name","logo","image"]

class IndexGoodsBannerAdmin(BaseModelAdmin):
    list_display = ["sku","image","index"]

class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    list_display = ["type","sku","display_type"]

class IndexPromotionBannerAdmin(BaseModelAdmin):
    list_display = ["name","image","index"]



admin.site.register(GoodsType,GoodsTypeAdmin)
admin.site.register(Goods)
admin.site.register(GoodsImage)
admin.site.register(GoodsSKU)
admin.site.register(IndexGoodsBanner,IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner,IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner,IndexPromotionBannerAdmin)

