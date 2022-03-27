import json

import requests

headers = {
    'Host': 'api.sfacg.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'content-type': 'application/x-www-form-urlencoded',
    'Accept': 'application/vnd.sfacg.api+json;version=1',
    'Accept-Language': 'zh-Hans-US;q=1',
    'Authorization': 'Basic YW5kcm9pZHVzZXI6MWEjJDUxLXl0Njk7KkFjdkBxeHE=',
    'User-Agent': "boluobao/4.8.42(android;22)/",
    "Cookie": ".SFCommunity=;session_APP=;",
}


def get(api_url: str, params: dict = None, **kwargs) -> dict:
    api_url = "https://api.sfacg.com/" + api_url.replace("https://api.sfacg.com/", '')
    return requests.get(api_url, params=params, headers=headers, timeout=10, **kwargs).json()


def post(api_url: str, data: dict = None, **kwargs) -> dict:
    api_url = "https://api.sfacg.com/" + api_url.replace("https://api.sfacg.com/", '')
    return requests.post(url=api_url, data=data, headers=headers, **kwargs).json()


def put(api_url: str, data: dict = None,  **kwargs) -> dict:
    api_url = "https://api.sfacg.com/" + api_url.replace("https://api.sfacg.com/", '')
    return requests.put(url=api_url, data=data, headers=headers, **kwargs).json()


class Task:
    @staticmethod
    def complete_task(tasks_id: str):
        return put(api_url="user/tasks/{}".format(tasks_id))

    @staticmethod
    def read_book_time(reading_date):
        read_time = {"seconds": 3605, "readingDate": reading_date, "entityType": 2}
        return put(api_url='user/readingtime', data=read_time)

    @staticmethod
    def receive_task(tasks_id: int, tasks_name: str):
        response = post("https://api.sfacg.com/user/tasks/{}".format(tasks_id))
        if response['status']['errorCode'] == 200:
            print('任务:{} 领取成功'.format(tasks_name))
        elif response['status']['errorCode'] == 798:
            print('任务:{} 今天已经领取过了,{}'.format(tasks_name, response['status']['msg']))
        else:
            print("msg:", response['status']['msg'], 'code:', response['status']['httpCode'])

    @staticmethod
    def complete_sign() -> None:
        return put(api_url='https://api.sfacg.com/user/signInfo')

    @staticmethod
    def share_task(uid: str):
        # {'taskId': 4, 'userId': uid, "env": 0}
        api_url = 'https://minipapi.sfacg.com/pas/mpapi/user/tasks?taskId=4&userId={}'.format(uid)
        return put(api_url=api_url, data=json.dumps({"env": 0}), headers='yes')


class User:

    @staticmethod
    def account_information():
        response, response2 = get(api_url='user'), get(api_url='user/money')
        return dict(response.get('data'), **response2.get('data'))

    @staticmethod
    def money_information():
        return get(api_url='user/money').get('data')

    @staticmethod
    def get_receive():
        return get(api_url='user/tasks?taskCategory=1&page=0&size=20').get('data')

def time_delta():
    from datetime import datetime, timedelta, timezone
    date_time = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
    return datetime.strftime(date_time, '%Y-%m-%d')


def shell_complete_task():
    print(time_delta())
    try:
        tasks_info_list = [[data['taskId'], data['name']] for data in User.get_receive()]
        Task.complete_sign()
        for tasks_info in tasks_info_list:
            Task.receive_task(*tasks_info)
        for tasks_id in tasks_info_list:
            """ShareTask"""
            # if tasks_id[0] == 4:
            #     # Task.share_task(str(User.account_information()['accountId']))
            #     Task.complete_task(tasks_id[0])
            # else:

            Task.read_book_time(time_delta())
            Task.complete_task(tasks_id[0])
            print('任务{}完成'.format(tasks_id[1]))
        print('已完成所有任务')
    except TypeError:
        return


if __name__ == '__main__':
    shell_complete_task()
