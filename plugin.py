from ncatbot.plugin_system import NcatBotPlugin, on_group_at
from .config_proxy import ProxiedPluginConfig
from dataclasses import dataclass, field
from ncatbot.core.event import GroupMessageEvent, MessageSegment, Reply, Image, Text
from typing import Optional
from ncatbot.utils import get_log

PLUGIN_NAME = "UnnamedImageSearchIntegrate"
logger = get_log(PLUGIN_NAME)


@dataclass
class SaucenaoConfig(ProxiedPluginConfig):
    api_token: str = field(default='')


@dataclass
class ImageSearchConfig(ProxiedPluginConfig):
    saucenao_config: SaucenaoConfig = field(default_factory=SaucenaoConfig)


class UnnamedImageSearchIntegrate(NcatBotPlugin):
    name = PLUGIN_NAME  # 必须，插件名称，要求全局独立
    version = "0.0.1"  # 必须，插件版本
    dependencies = {}  # 必须，依赖的其他插件和版本
    description = "集成搜图功能"  # 可选
    author = "default_user"  # 可选

    async def on_load(self) -> None:
        await super().on_load()

    async def on_close(self) -> None:
        await super().on_close()

    @on_group_at
    async def search_image(self, event: GroupMessageEvent):
        image_message: Optional[Image] = None
        has_command = False
        logger.debug(f'收到at消息, 开始解析')
        for message_segment in event.message:
            if message_segment.msg_seg_type == 'text':
                assert isinstance(message_segment, Text)
                if message_segment.text == 'si':
                    has_command = True
                continue
            if message_segment.msg_seg_type != 'reply':
                continue
            logger.debug(f'解析到引用消息段')
            assert isinstance(message_segment, Reply)
            cited_message = await self.api.get_msg(message_segment.id)
            logger.debug(f'获取到被引用消息id: {cited_message.message_id}')
            if len(cited_message.message.messages) != 1:
                logger.debug(f'被引用消息非单条消息, 数量: {len(cited_message.message.messages)}')
                continue
            if cited_message.message.messages[0].msg_seg_type != 'image':
                logger.debug(f'被引用消息非图片, 实际类型: {cited_message.message.messages[0].msg_seg_type}')
            single_cited_message = cited_message.message.messages[0]
            assert isinstance(single_cited_message, Image)
            image_message = single_cited_message
        if image_message is None:
            logger.debug(f'未置值')
            return
        if not has_command:
            logger.debug(f'未使用指令')
            return
        logger.debug(f'通过所有消息校验')
        await event.reply(f'收到搜图请求')
        logger.debug(f'图片url为: {image_message.url}')
