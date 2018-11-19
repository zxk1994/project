from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings

class FDFSStorage(Storage):
    """   fast dfs 文件存储类,必须含有open和save方法"""
    def __init__(self,client_conf=None,base_url=None):
        """  初始化 """
        if client_conf is None:
            client_conf=settings.FDFS_CLIENT_CONF
        self.client_conf= client_conf

        if base_url is None:
            # 这的路径必须写对，在settings设置
            base_url=settings.FDFS_URL
        self.base_url=base_url



    def _open(self,name,mode='rb'):
        #打开文件使用，rb:是以二进制的形式读取文件
        pass

    def _save(self,name,content):
        #保存文件使用，name：选择的上传文件的名字
        #content：包含你上传文件内容的File对象

        #创建一个Fdfs_client对象
        client=Fdfs_client(self.client_conf)
        #上传文件到系统中
        res=client.upload_by_buffer(content.read())

        # Ctrl+鼠标左击，可点击Fdfs_client去底层看返回值
        # @ return dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': local_file_name,
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # } if success else None

        if res.get('Status') !='Upload successed.':
            #上传失败
            raise Exception("上传文件到FastDFS失败")
        #获取返回的文件ID
        filename=res.get('Remote file_id')
        return filename

    def exists(self, name):
        # 判断文件名是否在系统存在，暂时给了个死值
        return False

    def url(self, name):
        # 返回访问文件的url路径
        return self.base_url+ name