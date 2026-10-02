from venv import create

from rest_framework import serializers
from .models import UserProfile, Category, SubCategory,Product, ProductImage, Review, Cart, CartItem, Favorite, FavoriteItem


from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('email', 'username', 'password', 'phone_number')
        extra_kwargs = {'password': {'write_only': True,}}

    def validate_email(self, value):
        if UserProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        username = validated_data.pop('username')
        user = UserProfile(email=email, username=username, **validated_data)
        user.set_password(password)
        user.save()
        return user

class CustomLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({"email": "Пользователь с таким email не найден"})

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Неверный пароль"})



        self.context['user'] = user
        return data

    def to_representation(self, instance):
        user = self.context['user']
        refresh = RefreshToken.for_user(user)

        return {
            'user': {
                'username': user.username,
                'email': user.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get('refresh')
        try:
            RefreshToken(token)
        except Exception:
            raise serializers.ValidationError({"refresh": "Невалидный токен"})
        return attrs

class UserProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id','first_name','last_name','avatar','status','phone_number','date_registered']

class UserProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields =  ['id','first_name','last_name','avatar','age','phone_number','date_registered']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields =['first_name','last_name']

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields =['id','category_name','category_image']

class SubCategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['subcategory_name']

class CategoryDetailSerializer(serializers.ModelSerializer):
    category_sub = SubCategorySimpleSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields =['category_name','category_image','category_sub']

class SubCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields =['id','category', 'subcategory_name','subcategory_image']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields =['product_image']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    created_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    class Meta:
        model = Review
        fields = ['review_image', 'comment', 'stars', 'created_time', 'user']
                                                                
class ProductListSerializer(serializers.ModelSerializer):
    subcategory = SubCategoryListSerializer()
    product_img = ProductImageSerializer(many=True, read_only=True)
    get_avg_rating = serializers.SerializerMethodField()
    get_count_rating = serializers.SerializerMethodField
    class Meta:
        model = Product
        fields = ['id','subcategory','product_name','product_img',
                  'get_avg_rating','get_count_rating','price']

    def get_avg_rating(self,obj):
        return obj.get_avg_rating()

    def get_count_rating(self,obj):
        return obj.get_avg_rating()


class SubCategoryDetailSerializer(serializers.ModelSerializer):
    sub_product =ProductListSerializer(many=True, read_only=True)
    class Meta:
        model = SubCategory
        fields =['subcategory_name','subcategory_image', 'sub_product']

class ProductDetailSerializer(serializers.ModelSerializer):
    subcategory = SubCategoryListSerializer()
    product_img = ProductImageSerializer(many=True, read_only=True)
    product_review = ReviewSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields =['id','subcategory','product_name','product_img''description',
                 'price','article','product_type','created_date']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),
                                                    write_only=True, source='product')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()


class CartSerializer(serializers.ModelSerializer):
    item = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'item', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()


class FavoriteItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),
                                                    write_only=True, source='product')
    class Meta:
        model = FavoriteItem
        fields = ['id', 'product', 'product_id']

class FavoriteSerializer(serializers.ModelSerializer):
    favorite_item = FavoriteItemSerializer(read_only=True, many=True)
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'favorite_item']


