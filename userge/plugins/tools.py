import os
import urbandict
from datetime import datetime
from . import get_all_plugins
from urllib.error import HTTPError
from userge import userge, Config


@userge.on_cmd("ping", about="check how long it takes to ping your userbot")
async def pingme(_, message):
    start = datetime.now()

    await message.edit('`Pong!`')

    end = datetime.now()
    ms = (end - start).microseconds / 1000

    await message.edit(f"**Pong!**\n`{ms} ms`")


@userge.on_cmd("help", about="to know how to use this")
async def helpme(_, message):
    cmd = message.matches[0].group(1)
    out_str = ""

    if cmd is None:
        out_str += "**which command you want ?**\n`.help command_name`\n\n"

        for cmd in sorted(userge.get_help()):
            out_str += f"**.{cmd}**\n"

    else:
        out = userge.get_help(cmd)
        out_str += f"**.{cmd}**\n\n__{out}__" if out else "__command not found!__"

    await message.edit(out_str)


@userge.on_cmd("json", about="replied msg to json")
async def jsonify(_, message):
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id
        the_real_message = message.reply_to_message

    else:
        the_real_message = message
        reply_to_id = message.message_id

    try:
        await message.edit(the_real_message)

    except Exception as e:
        with open("json.txt", "w+", encoding="utf8") as out_file:
            out_file.write(str(the_real_message))
        await userge.send_document(
            chat_id=message.chat.id,
            document="json.txt",
            caption=str(e),
            disable_notification=True,
            reply_to_message_id=reply_to_id
        )

        os.remove("json.txt")
        await message.delete()


@userge.on_cmd("all", about="to get all plugins")
async def getplugins(_, message):
    all_plugins = await get_all_plugins()

    out_str = "**All Userge Plugins**\n\n"

    for plugin in all_plugins:
        out_str += f"**{plugin}**\n"

    await message.edit(out_str)


@userge.on_cmd("del", about="to delete replied msg")
async def del_msg(_, message):
    msg_ids = [message.message_id]

    if message.reply_to_message:
        msg_ids.append(message.reply_to_message.message_id)

    await userge.delete_messages(message.chat.id, msg_ids)


@userge.on_cmd("ids", about="to get id")
async def getids(_, message):
    out_str = f"💁 Current Chat ID: `{message.chat.id}`"

    if message.reply_to_message:
        out_str += f"\n🙋‍♂️ From User ID: `{message.reply_to_message.from_user.id}`"
        file_id = None

        if message.reply_to_message.media:
            if message.reply_to_message.audio:
                file_id = message.reply_to_message.audio.file_id

            elif message.reply_to_message.document:
                file_id = message.reply_to_message.document.file_id

            elif message.reply_to_message.photo:
                file_id = message.reply_to_message.photo.file_id

            elif message.reply_to_message.sticker:
                file_id = message.reply_to_message.sticker.file_id

            elif message.reply_to_message.voice:
                file_id = message.reply_to_message.voice.file_id

            elif message.reply_to_message.video_note:
                file_id = message.reply_to_message.video_note.file_id

            elif message.reply_to_message.video:
                file_id = message.reply_to_message.video.file_id

            if file_id is not None:
                out_str += f"\n📄 File ID: `{file_id}`"

    await message.edit(out_str)


@userge.on_cmd("admins", about="to mention admins")
async def mentionadmins(client, message):
    mentions = "🛡 **Admin List** 🛡\n"
    input_str = message.matches[0].group(1)

    if input_str is None:
        input_str = message.chat.id

    try:
        async for x in client.iter_chat_members(chat_id=input_str, filter="administrators"):
            if x.status == "creator":
                mentions += "\n 👑 [{}](tg://user?id={}) `{}`".format(x.user.first_name, x.user.id, x.user.id)

            if x.status == "administrator":
                mentions += "\n ⚜ [{}](tg://user?id={}) `{}`".format(x.user.first_name, x.user.id, x.user.id)

    except Exception as e:
            mentions += " " + str(e) + "\n"

    await message.reply(mentions)
    await message.delete()


@userge.on_cmd("ub", about="Searches Urban Dictionary for the query")
async def urban_dict(_, message):
    await message.edit("Processing...")
    query = message.matches[0].group(1)

    if query is None:
        await message.edit(f"use `.ub query`")
        return

    try:
        mean = urbandict.define(query)

    except HTTPError:
        await message.edit(f"Sorry, couldn't find any results for: `{query}``")
        return

    meanlen = len(mean[0]["def"]) + len(mean[0]["example"])

    if meanlen == 0:
        await message.edit(f"No result found for **{query}**")
        return

    OUTPUT = f"**Query:** `{query}`\n\n**Meaning:** __{mean[0]['def']}__\n\n**Example:**\n__{mean[0]['example']}__"

    if len(OUTPUT) >= Config.MAX_MESSAGE_LENGTH:
        with open("output.txt", "w+", encoding="utf8") as out_file:
            out_file.write(str(OUTPUT))

        reply_to_id = message.reply_to_message.message_id \
            if message.reply_to_message \
                else message.message_id

        await userge.send_document(
            chat_id=message.chat.id,
            document="output.txt",
            caption=query,
            disable_notification=True,
            reply_to_message_id=reply_to_id
        )

        if os.path.exists("output.txt"):
            os.remove("output.txt")

        await message.delete()

    else:
        await message.edit(OUTPUT)