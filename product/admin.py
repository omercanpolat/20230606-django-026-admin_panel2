from django.contrib import admin
from .models import *
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from import_export import resources
from import_export.admin import ImportExportModelAdmin

admin.site.site_title = 'Clarusway Title'
admin.site.site_header = 'Clarusway Header'
admin.site.index_title = 'Clarusway Index Page'

# -----------------------------------------------------
# ProductModelAdmin

# Ürünlerin yorumlarını ürün-detay sayfasında göster:
class ReviewInline(admin.TabularInline):  # Alternatif: StackedInline (farklı görünüm aynı iş)
    model = Review # Model
    extra = 1 # Yeni ekleme için ekstra boş alan
    classes = ['collapse'] # Görüntülme tipi (default: tanımsız)

# Import-Export ModelResource:
class ProductModelResource(resources.ModelResource):
    class Meta:
        model = Product


class ProductModelAdmin(ImportExportModelAdmin):
    # Tablo sutunları:
    list_display = ['id', 'name', 'is_in_stock', 'create_date', 'update_date']
    # Tablo üzerinde güncelleyebilme:
    list_editable = ['is_in_stock']
    # Kayda gitmek için linkleme:
    list_display_links = ['id', 'name']
    # Filtreleme (arama değil):
    list_filter = [('name', DropdownFilter), 'is_in_stock', ('create_date', DateRangeFilter), ('update_date', DateTimeRangeFilter)]
    # Arama:
    search_fields = ['id', 'name']
    # Arama bilgilendirme yazısı: 
    search_help_text = 'Arama Yapmak için burayı kullanabilirsiniz.'
    # Default Sıralama:
    ordering = ['-create_date', '-id']
    # Sayfa başına kayıt sayısı:
    list_per_page = 20
    # Otomatik kaıyıt oluştur:
    prepopulated_fields = {'slug' : ['name']}
    # Tarihe göre filtreleme başlığı:
    date_hierarchy = 'create_date'
    # Resim gösterme read_only olarak çağır:
    readonly_fields = ["view_image"]
    # Form liste görüntüleme
    fields = (
        ('name', 'is_in_stock'),
        ('slug'),
        ('image', 'view_image'),
        ('description'),
        ('categories'),
    )
    '''
    # Detaylı form liste görüntüleme
    fieldsets = (
        (
            'General Settings', {
                "classes": ("wide",),
                "fields": (
                    ('name', 'slug'),
                    "is_in_stock"
                ),
            }
        ),
        (
            'Optionals Settings', {
                "classes": ("collapse",),
                "fields": ("description", "categories"),
                'description': "You can use this section for optionals settings"
            }
        ),
    )
    '''
    # İlişkili tablo (many2many) nasıl görünsün:
    filter_horizontal = ["categories"] # Yatay Görünüm
    # filter_vertical = ["categories"] # Dikey Görünüm
    # Ürün yorumlarını düzenle:
    inlines = [ReviewInline]
    # ImportExport:
    resource_class = ProductModelResource

    def set_stock_in(self, request, queryset):
        count = queryset.update(is_in_stock=True)
        self.message_user(request, f'{count} adet "Stokta Var" olarak işaretlendi.')
    

    def set_stock_out(self, request, queryset):
        count = queryset.update(is_in_stock=False)
        self.message_user(request, f'{count} adet "Stokta Yok" olarak işaretlendi.')

    actions = ('set_stock_in', 'set_stock_out')
    set_stock_in.short_description = 'İşaretli ürünleri stokta VAR olarak güncelle'
    set_stock_out.short_description = 'İşaretli ürünleri stokta YOK olarak güncelle'

    # Kaç gün önce eklendi:
    def added_days_ago(self, object):
        from django.utils import timezone
        different = timezone.now() - object.create_date
        return different.days
    
    # list_display = ['id', 'name', 'is_in_stock', 'added_days_ago', 'create_date', 'update_date']
    list_display += ['added_days_ago']

    # Kaçtane yorum var:
    def how_many_reviews(self, object):
        count = object.reviews.count()
        return count

    list_display += ['how_many_reviews']
    
    # Listede küçük resim göster:
    def view_image_in_list(self, obj):
        from django.utils.safestring import mark_safe
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} style="height:30px; width:30px;"></img>')
        return '-*-'

    list_display = ['view_image_in_list'] + list_display
    view_image_in_list.short_description = 'IMAGE'

admin.site.register(Product, ProductModelAdmin)

# -----------------------------------------------------
# ReviewModelAdmin

class ReviewModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_date', 'is_released')
    list_filter = [('product', RelatedDropdownFilter)]
    list_per_page = 50
    # raw_id_fields = ('product',) 

admin.site.register(Review, ReviewModelAdmin)

# -----------------------------------------------------
admin.site.register(Category)