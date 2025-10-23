
from rest_framework import serializers
from .models import Material

class MaterialSerializer(serializers.ModelSerializer):
    imagem_url = serializers.SerializerMethodField()
    class Meta:
        model = Material
        fields = ['id', 'nome', 'quantidade', 'imagem_url']

    def get_imagem_url(self, obj):
        request = self.context.get('request')
        if obj.imagem:
            url = obj.imagem.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None
