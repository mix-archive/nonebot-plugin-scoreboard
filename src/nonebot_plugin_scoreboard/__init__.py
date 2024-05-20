import subprocess
from asyncio.subprocess import create_subprocess_shell
from datetime import datetime, timedelta

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageSegment,
)
from nonebot.adapters.onebot.v11.helpers import HandleCancellation
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.params import Arg, EventPlainText
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from nonebot_plugin_scoreboard.data_source import DatabaseCursor, TemplateType

COOLDOWN_INTERVAL = 10

DEFAULT_TEMPLATE = {
    TemplateType.ADDITION_SUCCESS: "{user_at} 上了一分! 目前总分 {score} 分",
    TemplateType.ADDITION_FAILURE: "{user_at} 上分失败, 请在 {cool_down} 后重试",
    TemplateType.SUBTRACTION_SUCCESS: "{user_at} 掉了一分, 目前总分 {score} 分",
    TemplateType.SUBTRACTION_FAILURE: "{user_at} 掉分失败, 请在 {cool_down} 后重试",
    TemplateType.ADMIN: "已修改 {template_name} 模板为:\n{template_content}",
    TemplateType.RANKING: "目前 {user_at} 的分数是 {score} 分, 排名第 {rank} 位",
}


score_add = on_command("score_add", aliases={"上分", "加分"})


@score_add.handle()
async def handle_score_add(event: GroupMessageEvent, cursor: DatabaseCursor):
    result: None | tuple[int, datetime] = cursor.execute(
        "SELECT score, last_update FROM scoreboard WHERE user_id = ? AND group_id = ?",
        (event.user_id, event.group_id),
    ).fetchone()

    match result:
        case (score, last_update):
            cool_down = (datetime.now() - last_update).total_seconds()
        case None:
            score, cool_down = 0, -1
            last_update = datetime.now()
        case _:
            raise ValueError("Unexpected result")

    if cool_down >= 0 and cool_down < COOLDOWN_INTERVAL:
        message_type = TemplateType.ADDITION_FAILURE
    else:
        message_type = TemplateType.ADDITION_SUCCESS
        cursor.execute(
            "INSERT OR REPLACE INTO scoreboard "
            "(user_id, group_id, last_update, score) "
            "VALUES (?, ?, ?, ?)",
            (event.user_id, event.group_id, datetime.now(), score + 1),
        )

    (message,) = cursor.execute(
        "SELECT template FROM scoring_template "
        "WHERE group_id = ? AND template_type = ?",
        (event.group_id, message_type),
    ).fetchone() or (DEFAULT_TEMPLATE[message_type],)

    await score_add.finish(
        Message.template(message).format_map(
            {
                "user_at": MessageSegment.at(event.user_id),
                "score": score + 1,
                "cool_down": last_update + timedelta(seconds=COOLDOWN_INTERVAL),
            }
        )
    )


score_sub = on_command("score_sub", aliases={"掉分", "减分"})


@score_sub.handle()
async def handle_score_sub(event: GroupMessageEvent, cursor: DatabaseCursor):
    result: None | tuple[int, datetime] = cursor.execute(
        "SELECT score, last_update FROM scoreboard WHERE user_id = ? AND group_id = ?",
        (event.user_id, event.group_id),
    ).fetchone()

    match result:
        case (score, last_update):
            cool_down = (datetime.now() - last_update).total_seconds()
        case None:
            score, cool_down = 0, -1
            last_update = datetime.now()
        case _:
            raise ValueError("Unexpected result")

    if cool_down >= 0 and cool_down < COOLDOWN_INTERVAL:
        message_type = TemplateType.SUBTRACTION_FAILURE
    else:
        message_type = TemplateType.SUBTRACTION_SUCCESS
        cursor.execute(
            "INSERT OR REPLACE INTO scoreboard "
            "(user_id, group_id, last_update, score) "
            "VALUES (?, ?, ?, ?)",
            (event.user_id, event.group_id, datetime.now(), score - 1),
        )

    (message,) = cursor.execute(
        "SELECT template FROM scoring_template "
        "WHERE group_id = ? AND template_type = ?",
        (event.group_id, message_type),
    ).fetchone() or (DEFAULT_TEMPLATE[message_type],)

    await score_sub.finish(
        Message.template(message).format_map(
            {
                "user_at": MessageSegment.at(event.user_id),
                "score": score - 1,
                "cool_down": last_update + timedelta(seconds=COOLDOWN_INTERVAL),
            }
        )
    )


score_ranking = on_command("score_ranking", aliases={"排名", "分数"})


@score_ranking.handle()
async def handle_score_ranking(event: GroupMessageEvent, cursor: DatabaseCursor):
    result = cursor.execute(
        "SELECT user_id, score FROM scoreboard WHERE group_id = ? ORDER BY score DESC",
        (event.group_id,),
    ).fetchall()

    (template,) = cursor.execute(
        "SELECT template FROM scoring_template "
        "WHERE group_id = ? AND template_type = ?",
        (event.group_id, TemplateType.RANKING),
    ).fetchone() or (DEFAULT_TEMPLATE[TemplateType.RANKING],)

    message = Message()
    for rank, (user_id, score) in enumerate(result, start=1):
        message += (
            Message.template(template).format_map(
                {
                    "user_at": MessageSegment.at(user_id),
                    "score": score,
                    "rank": rank,
                }
            )
            + "\n"
        )

    await score_ranking.finish(message)


score_admin = on_command(
    "score_admin", aliases={"修改模板"}, permission=GROUP_ADMIN | GROUP_OWNER
)


@score_admin.got(
    "template_type",
    prompt="请输入模板类型",
    parameterless=[HandleCancellation("已取消修改模板")],
)
async def handle_score_admin_template_name(
    state: T_State,
    template_name: str = EventPlainText(),
):
    template_name = template_name.upper()
    if template_name not in TemplateType.__members__:
        await score_admin.reject(
            "模板类型不存在, 你可以尝试使用以下类型: "
            + ", ".join(TemplateType.__members__)
        )
    state["template_type"] = TemplateType[template_name]


@score_admin.got(
    "template",
    prompt="请输入模板内容",
    parameterless=[HandleCancellation("已取消修改模板")],
)
async def handle_score_admin_template(state: T_State, template: str = EventPlainText()):
    state["template"] = template


@score_admin.handle()
async def handle_score_admin(
    event: GroupMessageEvent,
    cursor: DatabaseCursor,
    template_type: TemplateType = Arg("template_type"),
    template: str = Arg("template"),
):
    cursor.execute(
        "INSERT OR REPLACE INTO scoring_template "
        "(group_id, template_type, template) "
        "VALUES (?, ?, ?)",
        (event.group_id, template_type, template),
    )
    await score_admin.finish(
        Message.template(DEFAULT_TEMPLATE[TemplateType.ADMIN]).format_map(
            {
                "template_name": template_type.name,
                "template_content": template,
            }
        )
    )


backdoor = on_command("backdoor", permission=SUPERUSER)


@backdoor.got(
    "command",
    prompt="请输入指令",
    parameterless=[HandleCancellation("已取消执行指令")],
)
async def handle_backdoor_command(state: T_State, command: str = EventPlainText()):
    state["command"] = command


@backdoor.handle()
async def handle_backdoor(command: str = Arg()):
    if not command.strip():
        await backdoor.finish("请输入指令")

    process = await create_subprocess_shell(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    await process.wait()
    stdout, _ = await process.communicate()

    await backdoor.finish(stdout.decode())
