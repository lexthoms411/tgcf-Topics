"""A bot to controll settings for tgcf live mode."""

import logging
import yaml
from telethon import events
from tgcf import config, const, plugins
from tgcf.bot.utils import (
    admin_protect,
    display_forwards,
    get_args,
    get_command_prefix,
    remove_source,
)
from tgcf.config import CONFIG, write_config
from tgcf.plugin_models import Style


@admin_protect
async def forward_command_handler(event):
    """Handle the `/forward` command."""
    notes = """The `/forward` command allows you to add a new forward.
    Example: suppose you want to forward from a to (b and c)

    ```
    /forward source: a
    dest: [b,c]
    ```

    a,b,c are chat ids

    """.replace(
        "    ", ""
    )

    try:
        args = get_args(event.message.text)
        if not args:
            raise ValueError(f"{notes}\n{display_forwards(config.CONFIG.forwards)}")

        parsed_args = yaml.safe_load(args)
        forward = config.Forward(**parsed_args)
        try:
            remove_source(forward.source, config.CONFIG.forwards)
        except:
            pass
        CONFIG.forwards.append(forward)
        config.from_to = await config.load_from_to(event.client, config.CONFIG.forwards)

        await event.respond("Success")
        write_config(config.CONFIG)
    except ValueError as err:
        logging.error(err)
        await event.respond(str(err))

    finally:
        raise events.StopPropagation

@admin_protect
async def remove_command_handler(event):
    """Handle the /remove command."""
    notes = """The `/remove` command allows you to remove a source from forwarding.
    Example: Suppose you want to remove the channel with id -100, then run

    `/remove source: -100`

    """.replace(
        "    ", ""
    )

    try:
        args = get_args(event.message.text)
        if not args:
            raise ValueError(f"{notes}\n{display_forwards(config.CONFIG.forwards)}")

        parsed_args = yaml.safe_load(args)
        source_to_remove = parsed_args["source"]
        remove_source(source_to_remove, config.CONFIG.forwards)
        config.from_to = await config.load_from_to(event.client, config.CONFIG.forwards)
        await event.respond("Success")
        write_config(config.CONFIG)
    except ValueError as err:
        logging.error(err)
        await event.respond(str(err))

    finally:
        raise events.StopPropagation

@admin_protect
async def topic_command_handler(event):
    """Handle the /topic command."""
    notes = """The `/topic` command allows you to manage topics.
    Example: suppose you want to add topics mapping

    ```
    /topic source: <source_id>
    topics_mapping:
      topic1: [dest_topic1, dest_topic2]
      topic2: [dest_topic3]
    ```

    <source_id> is the chat id, topics_mapping is a dictionary of source topics to lists of destination topics
    """.replace("    ", "")

    try:
        args = get_args(event.message.text)
        if not args:
            raise ValueError(f"{notes}")

        parsed_args = yaml.safe_load(args)
        source_id = parsed_args.get("source")
        topics_mapping = parsed_args.get("topics_mapping", {})
        if not source_id or not isinstance(topics_mapping, dict):
            raise ValueError(f"Invalid arguments\n{notes}")

        for forward in config.CONFIG.forwards:
            if forward.source == source_id:
                forward.topics_mapping = topics_mapping
                break
        else:
            raise ValueError(f"Source {source_id} not found")

        config.write_config(config.CONFIG)
        await event.respond("Topics updated successfully.")
    except ValueError as err:
        await event.respond(str(err))
    finally:
        raise events.StopPropagation

# Register the new handler
bot.add_event_handler(topic_command_handler, events.NewMessage(pattern='/topic'))
