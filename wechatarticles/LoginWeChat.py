# coding:  utf-8
import requests
import re


class LoginWeChat(object):
    """
    登录WeChat，获取更加详细的推文信息。如点赞数、阅读数、评论等
    article_url:
    http://mp.weixin.qq.com/s?__biz=MjM5NDU4ODI0NQ==&mid=2650949647&idx=1&sn=854714295ceee7943fe9426ab10453bf&chksm=bd739b358a041223833057cc3816f9562999e748904f39b166ee2178ce1a565e108fe364b920#rd'
    """

    def __init__(self, appmsg_token, cookie):
        """
        初始化参数
        Parameters
        ----------
        appmsg_token: str, 此处最好用r转义
            登录WeChat之后获取的appmsg_token
        cookie: str
            登录WeChat之后获取的cookie

        Returns
        -------
        None
        """
        self.s = requests.session()
        self.appmsg_token = appmsg_token
        self.headers = {
            "User-Agent":
            "Mozilla/5.0 (Linux; Android 7.1.1; PRO 6 Build/NMF26O; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0                   Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/043909 Mobile Safari/537.36  MicroMessenger/6.6.5.1280(0x26060532) NetType/WIFI Language",
            "Cookie":
            cookie
        }
        self.data = {
            "is_only_read": "1",
            "is_temp_url": "0",
        }

    def __verify(self, article_url):
        """
        简单验证文章url是否符合要求
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        None
        """
        verify_lst = ["mp.weixin.qq.com", "__biz", "mid", "sn", "idx"]
        for string in verify_lst:
            if string not in article_url:
                raise Exception(
                    "params is error, please check your article_url")

    def get_read_like_num(self, article_url):
        """
        获取阅读数和点赞数
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        (int, int):
            阅读数、点赞数
        """
        try:
            appmsgstat = self.GetSpecInfo(article_url)["appmsgstat"]
        except Exception:
            raise Exception("params is error, please check your article_url")
        return appmsgstat["read_num"], appmsgstat["like_num"]

    def get_comments(self, article_url):
        """
        获取文章评论
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        json:
            {
                "base_resp": {
                    "errmsg": "ok", 
                    "ret": 0
                }, 
                "elected_comment": [
                    {
                        "content": 用户评论文字, 
                        "content_id": "6846263421277569047", 
                        "create_time": 1520098511, 
                        "id": 3, 
                        "is_from_friend": 0, 
                        "is_from_me": 0, 
                        "is_top": 0, 
                        "like_id": 10001, 
                        "like_num": 3, 
                        "like_status": 0, 
                        "logo_url": "http://wx.qlogo.cn/mmhead/OibRNdtlJdkFLMHYLMR92Lvq0PicDpJpbnaicP3Z6kVcCicLPVjCWbAA9w/132", 
                        "my_id": 23, 
                        "nick_name": 评论用户的名字, 
                        "reply": {
                            "reply_list": [ ]
                        }
                    }
                ], 
                "elected_comment_total_cnt": 3, 评论总数
                "enabled": 1, 
                "friend_comment": [ ], 
                "is_fans": 1, 
                "logo_url": "http://wx.qlogo.cn/mmhead/Q3auHgzwzM6GAic0FAHOu9Gtv5lEu5kUqO6y6EjEFjAhuhUNIS7Y2AQ/132", 
                "my_comment": [ ], 
                "nick_name": 当前用户名, 
                "only_fans_can_comment": false
            }
        """
        __biz, _, idx, _ = self.__get_params(article_url)
        url = """
        https://mp.weixin.qq.com/mp/appmsg_comment?action=getcomment&__biz={}&idx={}&comment_id={}&limit=100&appmsg_token={}
        """.format(__biz, idx, self.__get_comment_id(article_url),
                   self.appmsg_token)

        comment_json = self.s.get(url, headers=self.headers).json()

        return comment_json

    def __get_comment_id(self, article_url):
        """
        获取comment_id
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        str:
            comment_id获取评论必要参数
        """
        res = self.s.post(article_url, data=self.data)
        comment_id = re.findall(r'comment_id = "\d+"',
                                res.text)[0].split(" ")[-1][1:-1]
        return comment_id

    def __get_params(self, article_url):
        """
        解析文章url, 获取必要的请求参数
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        (str, str, str, str):
            __biz, mid, idx, sn
        """
        # 进行简单验证文章的url
        self.__verify(article_url)
        string_lst = article_url.split("?")[1].split("&")
        dict_value = [string[string.index("=") + 1:] for string in string_lst]
        __biz, mid, idx, sn, *_ = dict_value
        if sn[-3] == "#":
            sn = sn[:-3]
        return __biz, mid, idx, sn

    def GetSpecInfo(self, article_url):
        """
        获取每篇文章具体信息
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        json:
            文章具体信息的json
            {
                'advertisement_info': [],
                'advertisement_num': 0,
                'appmsgstat': {'is_login': True,
                'like_num': 12,
                'liked': False,
                'read_num': 288,
                'real_read_num': 0,
                'ret': 0,
                'show': True},
                'base_resp': {'wxtoken': 2045685972},
                'reward_head_imgs': []
            }
        """
        __biz, mid, sn, idx = self.__get_params(article_url)
        origin_url = "http://mp.weixin.qq.com/mp/getappmsgext?"
        # string_lst = article_url.split("?")[1].split("&")
        # dict_value = [string[string.index("=") + 1:] for string in string_lst]
        # __biz, mid, idx, sn, *_ = dict_value
        # if sn[-3] == "#":
        #     sn = sn[:-3]
        appmsgext_url = origin_url + "__biz={}&mid={}&sn={}&idx={}&appmsg_token={}&x5=1".format(
            __biz, mid, sn, idx, self.appmsg_token)
        print(appmsgext_url)
        res = requests.post(
            appmsgext_url, headers=self.headers, data=self.data)
        print(res.url)
        return res.json()
