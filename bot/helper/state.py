from functools import partial

from bot import states_manager

class States:
    async def set(self, chat_id, state=None):
        if chat_id not in states_manager or not isinstance(states_manager[chat_id], dict):
            states_manager[chat_id] = {}

        if state is not None:
            states_manager[chat_id]["state"] = state

    def get(self, state):
        async def callback(event, state):
            if event.is_private and event.chat_id in states_manager:
                if "state" in states_manager[event.chat_id]:
                    return states_manager[event.chat_id]["state"] == state
            return False

        return partial(callback, state=state)

    async def add_data(self, pid, **kwargs):
        for key, value in kwargs.items():
            if pid in states_manager:
                if "data" in states_manager[pid]:
                    states_manager[pid]["data"][key] = value
                else:
                    states_manager[pid]["data"] = {key: value}
            else:
                states_manager[pid] = {"data": {key: value}}

    async def add_datas(self, pid, **kwargs):
        return await self.add_data(pid, **kwargs)

    async def get_data(self, pid, *keys):
        vals = []
        for key in keys:
            if pid in states_manager:
                if "data" in states_manager[pid]:
                    if key in states_manager[pid]["data"]:
                        vals.append(states_manager[pid]["data"][key])
                    else:
                        vals.append(None)
                else:
                    vals.append(None)
            else:
                vals.append(None)

        return vals[0] if len(vals) < 2 else vals

    async def get_datas(self, pid, *keys):
        return await self.get_data(pid, *keys)

    async def finish(self, chat_id, del_data=True):
        if chat_id in states_manager:
            if "data" in states_manager[chat_id] and not del_data:
                if "state" in states_manager[chat_id]:
                    states_manager[chat_id].pop("state")
            else:
                states_manager.pop(chat_id)

states = States()