
EVENT_TYPES = {
    "Experiment": 
        {
            "prompt": [
                "Countries, organizations, institutions, or companies verify whether the equipment is qualified based on existing standards, including but not limited to flights, launching, testing, etc.",
                "Similar triggers such as experiment, test.", 
            ],
            "positive": [
                "Event trigger is <Triggers>.", 
                "<Subject> experimented with <Equipment> in <Location> on <Date>."
            ],
            "negative": [
                "Event trigger is <Trigger>.", 
            ],
        },
    "Manoeuvre": 
        {
            "prompt": [
                "Exercises conducted in the course of campaigns and battles, in the context of the situation envisaged, and are the highest and most centralized form of military training.",
                "Similar triggers such as move.", 
            ],
            "positive": [
                "Event trigger is <Triggers>.", 
                "<Subject> manoeuvered <Content> from <Area> on <Date>."
            ],
            "negative": [
                "Event trigger is <Trigger>.", 
            ],
        },
    "Deploy": 
        {
            "prompt": [
                "The movement of military forces, i.e., personnel or equipment, within a country or organization.",
                "Similar triggers such as move.", 
            ],
            "positive": [
                "Event trigger is <Triggers>.", 
                "<Subject> deployed <Militaryforce> on <Location> on <Date>."
            ],
            "negative": [
                "Event trigger is <Trigger>.", 
            ],
        },
    "Support": 
        {
            "prompt": [
                "Subject provides material help or relief actions to the object.",
                "Similar triggers such as helped, aided.", 
            ],
            "positive": [
                "Event trigger is <Triggers>.", 
                "<Subject> supported <Object> using <Materials> on <Date>."
            ],
            "negative": [
                "Event trigger is <Trigger>.", 
            ],
        },
    "Accident": 
        {
            "prompt": [
                "Accidents that happen unexpectedly.",
                "Similar triggers such as unexpected, accident.", 
            ],
            "positive": [
                "Event trigger is <Triggers>.", 
                "<Subject> accidentally caused <Result> in <Location> on <Date>."
            ],
            "negative": [
                "Event trigger is <Trigger>.", 
            ],
        },
    "Exhibit": 
        {
            "prompt": [
                "Countries, organizations, institutions, companies, etc. exhibit or publicize equipment, products, etc. through airshows or other forms.",
                "Similar triggers such as show, exhibit.", 
            ],
            "positive": [
                "Event trigger is <Triggers>.", 
                "<Subject> shown <Equipment> in <Location> on <Date>."
            ],
            "negative": [
                "Event trigger is <Trigger>.", 
            ],
        },
    "Conflict": 
        {
            "prompt": [
                "Violence acts, such as attack, that causes damage or injury, or a conflict or confrontation between two parties, such as protest or condemnation.",
                "Similar triggers such as attack.", 
            ],
            "positive": [
                "Event trigger is <Triggers>.", 
                "<Subject> attacked <Object> in <Location> on <Date>."
            ],
            "negative": [
                "Event trigger is <Trigger>.", 
            ],
        },
    "Injure": 
        {
            "prompt": [
                "Person entity suffered physical injury.",
                "Similar triggers such as injury, injure, hurt.", 
            ],
            "positive": [
                "Event trigger is <Triggers>.", 
                "<Subject> injured <Quantity> in <Location> on <Date>."
            ],
            "negative": [
                "Event trigger is <Trigger>.", 
            ],
        },
}
ROLE_NAMES = [
    "Subject", 
    "Equipment",
    "Date",
    "Location",
    "Content",
    "Object",
    "Militaryforce",
    "Quantity",
    "Result",
    "Area", 
    "Materials"
]


ROLE_NAMEs_MAP = {"Triggers": "Trigger"}
for rn in ROLE_NAMES:
    if rn in ["Subject"]:
        ROLE_NAMEs_MAP[rn] = "some one"
    if rn in ["Equipment", "Object", "Content", "Result", "Materials", "Militaryforce"]:
        ROLE_NAMEs_MAP[rn] = "some thing"
    if rn in ["Date"]:
        ROLE_NAMEs_MAP[rn] = "some time"
    if rn in ["Location", "Area"]:
        ROLE_NAMEs_MAP[rn] = "some place"
    if rn in ["Quantity"]:
        ROLE_NAMEs_MAP[rn] = "some quantity"

for t in list(EVENT_TYPES.keys()):
    changed_prompt = EVENT_TYPES[t]['positive']
    changed_prompt = "\n".join(changed_prompt)
    for rn in ROLE_NAMES:
        if rn in changed_prompt:
            replacement = ROLE_NAMEs_MAP[rn]
            changed_prompt = changed_prompt.replace(f"<{rn}>", replacement)
    
    if "Triggers" in changed_prompt:
        changed_prompt = changed_prompt.replace(f"<Triggers>", "<Trigger>")
    changed_prompt = changed_prompt.split("\n") 
    EVENT_TYPES[t]['prompt'] = EVENT_TYPES[t]['prompt'][:2] + changed_prompt
    
print(EVENT_TYPES)




# EVENT_TYPES = {
#     "Experiment": 
#         {
#             "prompt": [
#                 "国家、组织、机构或公司根据现有标准验证设备是否合格，包括但不限于飞行、发射、测试等。",
#                 "类似触发词如实验、测试。",
#             ],
#             "positive": [
#                 "事件触发词是 <Triggers>", 
#                 "<Subject> 在 <Location> 于 <Date> 进行了 <Equipment> 实验。"
#             ],
#             "negative": [
#                 "事件触发词是 <Trigger>", 
#             ],
#         },
#     "Manoeuvre": 
#         {
#             "prompt": [
#                 "在设想的情境下进行的战役和战斗过程中的演习，是最高级别和最集中化的军事训练形式。",
#                 "类似触发词如移动。",
#             ],
#             "positive": [
#                 "事件触发词是 <Triggers>", 
#                 "<Subject> 于 <Date> 从 <Area> 演习了 <Content>。"
#             ],
#             "negative": [
#                 "事件触发词是 <Trigger>", 
#             ],
#         },
#     "Deploy": 
#         {
#             "prompt": [
#                 "军事力量的移动，即人员或设备在国家或组织内部的移动。",
#                 "类似触发词如移动。",
#             ],
#             "positive": [
#                 "事件触发词是 <Triggers>", 
#                 "<Subject> 于 <Date> 在 <Location> 部署了 <Militaryforce>。"
#             ],
#             "negative": [
#                 "事件触发词是 <Trigger>", 
#             ],
#         },
#     "Support": 
#         {
#             "prompt": [
#                 "主体向客体提供物质帮助或救援行动。",
#                 "类似触发词如帮助、援助。",
#             ],
#             "positive": [
#                 "事件触发词是 <Triggers>", 
#                 "<Subject> 于 <Date> 使用 <Materials> 支持了 <Object>。"
#             ],
#             "negative": [
#                 "事件触发词是 <Trigger>", 
#             ],
#         },
#     "Accident": 
#         {
#             "prompt": [
#                 "意外发生的事故。",
#                 "类似触发词如意外、事故。",
#             ],
#             "positive": [
#                 "事件触发词是 <Triggers>", 
#                 "<Subject> 于 <Date> 在 <Location> 意外导致了 <Result>。"
#             ],
#             "negative": [
#                 "事件触发词是 <Trigger>", 
#             ],
#         },
#     "Exhibit": 
#         {
#             "prompt": [
#                 "国家、组织、机构、公司等通过航展或其他形式展览或宣传设备、产品等。",
#                 "类似触发词如展示、展览。",
#             ],
#             "positive": [
#                 "事件触发词是 <Triggers>", 
#                 "<Subject> 于 <Date> 在 <Location> 展示了 <Equipment>。"
#             ],
#             "negative": [
#                 "事件触发词是 <Trigger>", 
#             ],
#         },
#     "Conflict": 
#         {
#             "prompt": [
#                 "暴力行为，如攻击，造成损害或伤害，或双方之间的冲突或对抗，如抗议或谴责。",
#                 "类似触发词如攻击。",
#             ],
#             "positive": [
#                 "事件触发词是 <Triggers>", 
#                 "<Subject> 于 <Date> 在 <Location> 攻击了 <Object>。"
#             ],
#             "negative": [
#                 "事件触发词是 <Trigger>", 
#             ],
#         },
#     "Injure": 
#         {
#             "prompt": [
#                 "人物实体遭受身体伤害。",
#                 "类似触发词如受伤、伤害。",
#             ],
#             "positive": [
#                 "事件触发词是 <Triggers>", 
#                 "<Subject> 于 <Date> 在 <Location> 受伤了 <Quantity>。"
#             ],
#             "negative": [
#                 "事件触发词是 <Trigger>", 
#             ],
#         },
# }
# ROLE_NAMES = [
#     "Subject", 
#     "Equipment",
#     "Date",
#     "Location",
#     "Content",
#     "Object",
#     "Militaryforce",
#     "Quantity",
#     "Result",
# ]

# ROLE_NAMEs_MAP = {"Triggers": "扳机"}
# for rn in ROLE_NAMES:
#     if rn in ["Subject"]:
#         ROLE_NAMEs_MAP[rn] = "某人"
#     if rn in ["Equipment", "Object", "Content", "Result", "Militaryforce"]:
#         ROLE_NAMEs_MAP[rn] = "某物"
#     if rn in ["Date"]:
#         ROLE_NAMEs_MAP[rn] = "某个时间"
#     if rn in ["Location"]:
#         ROLE_NAMEs_MAP[rn] = "某个地方"
#     if rn in ["Quantity"]:
#         ROLE_NAMEs_MAP[rn] = "一些数字"

# for t in list(EVENT_TYPES.keys()):
#     changed_prompt = EVENT_TYPES[t]['positive']
#     changed_prompt = "\n".join(changed_prompt)
#     for rn in ROLE_NAMES:
#         if rn in changed_prompt:
#             replacement = ROLE_NAMEs_MAP[rn]
#             changed_prompt = changed_prompt.replace(f"<{rn}>", replacement)
    
#     if "Triggers" in changed_prompt:
#         changed_prompt = changed_prompt.replace(f"<Triggers>", "<Trigger>")
#     changed_prompt = changed_prompt.split("\n") 
#     EVENT_TYPES[t]['prompt'] = EVENT_TYPES[t]['prompt'][:2] + changed_prompt
