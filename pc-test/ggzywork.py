from celery import Celery
from kombu import Exchange, Queue
import config
from biz import ggzybiz
from utils import util
import logging

# 启动命令
# celery -A  ggzywork worker -P eventlet -c 3 --loglevel=info
app = Celery()
QueueName = "ggzywork"
app.conf.update(
    # 中间人设置
    BROKER_URL=config.MQ.url,
    # 配置序列化任务载荷的默认的序列化方式
    CELERY_TASK_SERIALIZER='json',
    # 忽略接收其他内容
    CELERY_ACCEPT_CONTENT=['json'],
    # 结果序列号
    CELERY_RESULT_SERIALIZER='json',
    # 设置时区
    CELERY_TIMEZONE='Asia/Shanghai',
    # 使用UTC的方式，UTC的时间、时区、时差
    CELERY_ENABLE_UTC=True,
    # 配置队列
    CELERY_QUEUES=(
        Queue(QueueName, Exchange(QueueName), routing_key=QueueName),
    ),
    # 默认队列
    CELERY_DEFAULT_QUEUE=QueueName,
    # 连接方式
    CELERY_DEFAULT_EXCHANGE_TYPE='direct',
    # 路由队列
    CELERY_DEFAULT_ROUTING_KEY=QueueName,
    # 任务执行结果的超时时间
    CELERY_TASK_RESULT_EXPIRES=1800,
    # worker 每次取任务的数量
    CELERYD_PREFETCH_MULTIPLIER=1,
    # 每个worker最多执行完10个任务就会被销毁,可防止内存泄露
    CELERYD_MAX_TASKS_PER_CHILD=10,
    #  非常重要,有些情况下可以防止死锁
    CELERYD_FORCE_EXECV=True,
    # 可以让Celery更加可靠,只有当worker执行完任务后,才会告诉MQ,消息被消费
    CELERY_ACKS_LATE=True,
    # 单个任务的运行时间不超过此值，否则会被SIGKILL 信号杀死
    CELERYD_TASK_TIME_LIMIT=600,
    #  任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
    CELERY_DISABLE_RATE_LIMITS=True
)


@app.task
def hello(page):
    util.logger.warning("start")
    g = ggzybiz.GgzyBiz()
    g.main(page)
    return 'end'
