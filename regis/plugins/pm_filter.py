import ast
import asyncio
import logging
import re

import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, MessageNotModified, PeerIdInvalid, UserIsBlocked
from pyrogram.errors.exceptions.bad_request_400 import (
    MediaEmpty,
    PhotoInvalidDimensions,
    WebpageMediaEmpty,
)
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from regis.database.connections_mdb import (
    active_connection,
    all_connections,
    delete_connection,
    if_active,
    make_active,
    make_inactive,
)
from regis.database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from regis.database.ia_filterdb import Media, get_file_details, get_search_results
from regis.database.users_chats_db import db
from regis.info import (
    ADMINS,
    AUTH_CHANNEL,
    AUTH_GROUPS,
    AUTH_USERS,
    AUTO_DELETE_MESSAGE_TIME,
    CUSTOM_FILE_CAPTION,
    IGNORE_WORDS,
    IMDB,
    IMDB_TEMPLATE,
    LOG_CHANNEL,
    MAINTENANCE_MODE,
    P_TTI_SHOW_OFF,
    PM_FILTER,
    PROTECT_CONTENT,
    SINGLE_BUTTON,
    SPELL_CHECK_REPLY,
    SUPPORT_CHAT,
)
from regis.Script import script
from regis.utils import (
    get_poster,
    get_settings,
    get_size,
    is_subscribed,
    save_group_settings,
    search_gagala,
    temp,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
BUTTONS = {}
SPELL_CHECK = {}


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if MAINTENANCE_MODE:
        if AUTH_USERS and message.from_user and message.from_user.id in AUTH_USERS:
            k = await manual_filters(client, message)
            if k == False:
                await auto_filter(client, message)
        else:
            btn = [
        [
            InlineKeyboardButton('⚡️ ℂ𝕀ℕ𝔼𝕄𝔸 ℍ𝕌𝔹 ⚡️', url=f'https://t.me/cinemaforyou07')
        ]
        ]
        await message.reply_text(f"🔰𝗡𝗢𝗧𝗜𝗖𝗘🔰\n\nService is 𝕔𝕝𝕠𝕤𝕖𝕕 for 𝟮 𝘄𝗲𝗲𝗸𝘀.\nwill start again by <u>next month.</u>.\n\n𝖡𝗒 𝗍𝗁𝗂𝗌 𝗍𝗂𝗆𝖾, 𝖬𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 <b>you have 𝗌𝗎𝖻𝗌𝖼𝗋𝗂𝖻𝖾𝖽 CINEMA HUB group👇🏻</b>", reply_markup=InlineKeyboardMarkup(btn))    
    else:
        k = await manual_filters(client, message)
        if k == False:
            await auto_filter(client, message)




@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    ad_user = query.from_user.id
    if int(ad_user) in ADMINS:
        pass
    elif int(req) not in [query.from_user.id, 0]:
        return await query.answer(
            "All right, but this is not yours.;\nNice Try! But, This Was Not Your Request, Request Yourself;",
            show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer(f"⚠️ Hey, {query.from_user.first_name}! You are using one of my old messages, send the request again ⚠️", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Pages {round(int(offset) / 10) + 1} / {round(total / 10)}",
                                  callback_data="pages")]
        )
        btn.append(
                [InlineKeyboardButton(text="⭕️ ℂℍ𝔼ℂ𝕂 ℙ𝕄 ⭕️", url=f"https://telegram.dog/{temp.U_NAME}")]
            )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("𝗡𝗘𝗫𝗧 ⏩", callback_data=f"next_{req}_{key}_{n_offset}")])
        btn.append(
                [InlineKeyboardButton(text="⭕️ ℂℍ𝔼ℂ𝕂 ℙ𝕄 ⭕️", url=f"https://telegram.dog/{temp.U_NAME}")]
            )
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("𝗡𝗘𝗫𝗧 ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
        btn.append(
                [InlineKeyboardButton(text="⭕️ ℂℍ𝔼ℂ𝕂 ℙ𝕄 ⭕️", url=f"https://telegram.dog/{temp.U_NAME}")]
            )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    ad_user = query.from_user.id
    if int(ad_user) in ADMINS:
        pass
    elif int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("okDa", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.message_id)
    if not movies:
        return await query.answer(f"⚠️ Hey, {query.from_user.first_name}! You are clicking on an old button which is expired ⚠️", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking my database...')
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            await query.message.edit(f'╭───────────\n\n.\n├• 🧑🏽‍💻 May be it is not uploaded. Wait until admin uploads.\n.\n.\n.\n├• 𝗜𝗳 𝗶𝘁 𝗶𝘀 𝗮 𝘀𝗲𝗿𝗶𝗲𝘀, 𝘁𝗵𝗲𝗻 𝗹𝗼𝗼𝗸 𝗶𝗳 𝗮𝗻𝗼𝘁𝗵𝗲𝗿 𝗕𝗼𝘁 𝗴𝗮𝘃𝗲 𝗶𝘁 𝘁𝗼 𝘆𝗼𝘂.\n.')
            jj = await bot.send_message(LOG_CHANNEL,f'New Request of {query.from_user.first_name}\n\n<b>✘Link</b> :-\n{query.message.reply_to_message.link}', disable_web_page_preview= True)
            await asyncio.sleep(1800)
            await jj.delete()
            #await query.message.reply_to_message.delete()
            #await query.message.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('*')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer('*')

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('*')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == "creator") or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer(f"🤒 Hey, You need to be Group Owner or an Auth User to do that! 🤒",show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == "creator") or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer(f"⚠️ Hey, {query.from_user.first_name}! That's not for you!! ⚠️",show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode="md"
        )
        return await query.answer('*')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode="md")
        return await query.answer('*')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode="md"
            )
        return await query.answer('*')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode="md"
            )
        return await query.answer('*')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('*')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        user = query.message.reply_to_message.from_user.id
        ad_user = query.from_user.id
        if int(ad_user) in ADMINS:
            pass
        elif int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(
                "All right, but this is not yours.;\nNice Try! But, This Was Not Your Request, Request Yourself;",
                show_alert=True)
        if not files_:
            return await query.answer('No such file exists.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        buttons = [
            [
            InlineKeyboardButton('⚡️𝕁𝕠𝕚𝕟 ℂ𝕚𝕟𝕖𝕙𝕦𝕓 𝕗𝕠𝕣 𝕞𝕠𝕣𝕖⚡️', url=f'https://t.me/cinemaforyou07')]
            ]
            
        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://tnlink.in/st?api=ea95aad94bdb11a4c3703275264f4406d9240276&url=https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://tnlink.in/st?api=ea95aad94bdb11a4c3703275264f4406d9240276&url=https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    protect_content=True if ident == "filep" else False,
                )
                await query.answer(f'Hey {query.from_user.first_name} ℂℍ𝔼ℂ𝕂 ℙ𝕄, I have sent files',show_alert = True)
                await client.send_message(LOG_CHANNEL,f'╭───#Got_file──〄\n│\n├• <b>{query.from_user.first_name}</b>\n│\n├•<a href= http://www.example.com/>File name:</a> <code>{files.file_name}</code>\n.')
               # await client.send_message(chat_id=query.from_user.id,text='Please join my main group and request there from future.\n Join via below button👇🏻',reply_markup=InlineKeyboardMarkup(buttons))
        except UserIsBlocked:
            await query.answer(f'Hey {query.from_user.first_name} Unblock the bot mahn !',show_alert = True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer(f"Hey, {query.from_user.first_name}! I Like Your Smartness, But Don't Be Oversmart 😒",show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        buttons = [
            [InlineKeyboardButton('⚡️𝕁𝕠𝕚𝕟 ℂ𝕚𝕟𝕖𝕙𝕦𝕓 𝕗𝕠𝕣 𝕞𝕠𝕣𝕖⚡️', url=f'https://tnlink.in/st?api=ea95aad94bdb11a4c3703275264f4406d9240276&url=https://t.me/cinemaforyou07')]
            ]
        await query.answer()
        await client.send_message(LOG_CHANNEL,f'╭───#Got_file──〄\n│\n├• <b>{query.from_user.first_name}</b>\n│\n├•<a href= http://www.example.com/>File name:</a> <code>{files.file_name}</code>\n.')
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            reply_markup=InlineKeyboardMarkup(buttons),
            protect_content=True if ident == 'checksubp' else False
        )
      #  await client.send_message(chat_id=query.from_user.id,text='Please join my main group and request there from future.\n Join via below button👇🏻',reply_markup=InlineKeyboardMarkup(buttons))
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
        InlineKeyboardButton('➕ 𝔸𝕕𝕕 𝕄𝕖 𝕋𝕠 𝕐𝕠𝕦𝕣 ℂ𝕙𝕒𝕥 ➕', url=f'https://tnlink.in/st?api=ea95aad94bdb11a4c3703275264f4406d9240276&url=http://t.me/{temp.U_NAME}?startgroup=true')
        ],[
        InlineKeyboardButton('  𝕁𝕠𝕚𝕟 ℂ𝕚𝕟𝕖𝕙𝕦𝕓 ', url=f'https://t.me/cinemaforyou07')],
        [InlineKeyboardButton('𝕌𝕡𝕕𝕒𝕥𝕖 ℂ𝕙𝕒𝕟𝕟𝕖𝕝', url='https://t.me/cinemahub02')
        ],
        [
        InlineKeyboardButton('𝔸𝕓𝕠𝕦𝕥', callback_data='about'),
        InlineKeyboardButton('𝕊𝕠𝕦𝕣𝕔𝕖', callback_data='source')
        ],[InlineKeyboardButton('ℹ️ ℂ𝕠𝕞𝕞𝕒𝕟𝕕𝕤 ℹ️', url='https://tnlink.in/st?api=ea95aad94bdb11a4c3703275264f4406d9240276&url=https://soymadip.github.io/Regis/commands')] 
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
        await query.answer('HOME')
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('admin', callback_data='admin'),
            InlineKeyboardButton('connect', callback_data='coct'),
            InlineKeyboardButton('filters', callback_data='auto_manual'),
            ],[
            InlineKeyboardButton('gtrans', callback_data='gtrans'),
            InlineKeyboardButton('info', callback_data='info'),
            InlineKeyboardButton('memes', callback_data='memes'),
            ],[
            InlineKeyboardButton('paste', callback_data='paste'),
            InlineKeyboardButton('password gen', callback_data='genpassword'),
            InlineKeyboardButton('pin', callback_data='pin'),
            ],[
            InlineKeyboardButton('purge', callback_data='purge'),
            InlineKeyboardButton('restric', callback_data='restric'),
            InlineKeyboardButton('search', callback_data='search'),
            ],[
            InlineKeyboardButton('share text', callback_data='sharetext'),
            InlineKeyboardButton('music', callback_data='music'),
            InlineKeyboardButton('tt-speech', callback_data='tts'),
            ],[
            InlineKeyboardButton('tgraph', callback_data='tgraph'),
            InlineKeyboardButton('url shortner', callback_data='shortner'),
            InlineKeyboardButton('zombies', callback_data='zombies'),
            ],[
            InlineKeyboardButton('« Back', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "about":
        buttons = [[
        InlineKeyboardButton('✗ Updates ✗', url='https://t.me/cinemahub02'),
        InlineKeyboardButton('✗ Source ✗', callback_data='source')
    ], [
        InlineKeyboardButton('✗ Back ✗', callback_data='start'),
        InlineKeyboardButton('✗ Close ✗', callback_data='close_data')
    ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('« Back', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("First use /connect <group id>.")
            return await query.answer('*')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["botpm"] else '❌ No',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer('Done')


async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if message.text.startswith("#"): return  # ignore wrong formats
        if message.text.startswith("."): return # ignore userbot commands
        if re.findall(r"((^/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 1 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(msg)
                else:
                    return
        else:
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
            ]
            for file in files
        ]

    if offset != "":
        key = f"{message.chat.id}-{message.message_id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
                [InlineKeyboardButton(text="⭕️ ℂℍ𝔼ℂ𝕂 ℙ𝕄 ⭕️", url=f"https://telegram.dog/{temp.U_NAME}")]
            )
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{round(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="𝗡𝗘𝗫𝗧 ⏩", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
                [InlineKeyboardButton(text="⭕️ ℂℍ𝔼ℂ𝕂 ℙ𝕄 ⭕️", url=f"https://telegram.dog/{temp.U_NAME}")]
            )
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    reply_id = message.reply_to_message.message_id if message.reply_to_message else message.message_id
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"\n<b>️📽️ℝ𝕖𝕢𝕦𝕖𝕤𝕥𝕖𝕕 𝕄𝕠𝕧𝕚𝕖 </b> : {search}\n<b>👤ℝ𝕖𝕢𝕦𝕖𝕤𝕥𝕖𝕕 𝕓𝕪 </b> : {message.from_user.mention}\n\n⚙️<b>𝗧𝗵𝗶𝘀 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝘄𝗶𝗹𝗹 𝗯𝗲 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗮𝗳𝘁𝗲𝗿 𝟮 𝗺𝗶𝗻𝘂𝘁𝗲𝘀.</b>\n\n<b>Watch this to know How to get files:-</b>\nhttps://t.me/cinemahub02/60"
    if imdb and imdb.get('poster'):
        try:
            hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024], reply_to_message_id=reply_id, reply_markup=InlineKeyboardMarkup(btn))
            await asyncio.sleep(AUTO_DELETE_MESSAGE_TIME)
            await hehe.delete()
            await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await message.reply_photo(photo=poster, caption=cap[:1024], reply_to_message_id=reply_id, reply_markup=InlineKeyboardMarkup(btn))
            await asyncio.sleep(60)
            await hmm.delete()
            await message.delete()
        except Exception as e:
            logger.exception(e)
            fek = await message.reply_photo(photo="https://telegra.ph/file/4e7e0a76a54d16ce2b80c.jpg", caption=cap, reply_to_message_id=reply_id, reply_markup=InlineKeyboardMarkup(btn))
            await asyncio.sleep(60)
            await fek.delete()
            await msg.delete()
    else:
        fuk = await message.reply_photo(photo="https://telegra.ph/file/4e7e0a76a54d16ce2b80c.jpg", caption=cap, reply_to_message_id=reply_id, reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(60)
        await fuk.edit(f"\n \n⚙️ {message.from_user.mention}'s Result For **{search}**  Closed ️")
    if spoll:
        await msg.message.edit(f"\n \n⚙️ Result  Closed ️")




async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply("🤖Checking.....") #IF not found movie.
        await k.delete()
        return
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True)  # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        k = await msg.reply(".")   #if not found at IMDB
        await asyncio.sleep(1)
        await k.delete()
        return
    SPELL_CHECK[msg.message_id] = movielist
    btn = [[
        InlineKeyboardButton(
            text=movie.strip(),
            callback_data=f"spolling#{user}#{k}",
        )
    ] for k, movie in enumerate(movielist)]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    m = await msg.reply(f"I couldn't find your movie.😑\n\n<b>Did you want any of these</b>👇", reply_markup=InlineKeyboardMarkup(btn))
    await asyncio.sleep(15)
    await m.delete()

    


async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.message_id if message.reply_to_message else message.message_id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            dd = await message.reply_text(
                             reply_text.format(
                                 first = message.from_user.first_name,
                                 username = None if not message.from_user.username else '@' + message.from_user.username,
                                 mention = message.from_user.mention,
                                 id = message.from_user.id,
                                 dcid = message.from_user.dc_id,
                                 chatname = message.chat.title,
                                 query = name
                             ),
                             group_id,
                             disable_web_page_preview=True,
                             reply_to_message_id=reply_id
                            )
                            await asyncio.sleep(7200)
                            await dd.edit(f"\n \n⚙️ Result  Closed ️")
                        else:
                            button = eval(btn)
                            mm = await message.reply_text(
                                reply_text.format(
                                    first = message.from_user.first_name,
                                    username = None if not message.from_user.username else '@' + message.from_user.username,
                                    mention = message.from_user.mention,
                                    id = message.from_user.id,
                                    dcid = message.from_user.dc_id,
                                    chatname = message.chat.title,
                                    query = name
                                ),
                                group_id,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id = reply_id
                            )
                            await asyncio.sleep(7200)
                            await mm.edit(f"\n \n⚙️ Result  Closed ️")
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text.format(
                                first = message.from_user.first_name,
                                last = message.from_user.last_name,
                                username = None if not message.from_user.username else '@' + message.from_user.username,
                                mention = message.from_user.mention,
                                id = message.from_user.id,
                                dcid = message.from_user.dc_id,
                                chatname = message.chat.title,
                                query = name
                            ) or "",
                            reply_to_message_id = reply_id
                        )
                    else:
                        button = eval(btn) 
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text.format(
                                first=message.from_user.first_name,
                                last=message.from_user.last_name,
                                username = None if not message.from_user.username else '@' + message.from_user.username,
                                mention = message.from_user.mention,
                                id=message.from_user.id,
                                dcid = message.from_user.dc_id,
                                chatname = message.chat.title,
                                query = name
                            ) or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id = reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
