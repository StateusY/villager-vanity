# inspired by crop_and_kettle

from beet import (
    Context,
    FileDeserialize,
    JsonFileBase,
    NamespaceFileScope,
    LootTable,
    Recipe,
    ItemModel,
    Model,
    Language,
    Advancement,
    Function
)
from pydantic import BaseModel, Field
from typing import ClassVar, Literal
from PIL import Image
import logging
import copy

class Hat(BaseModel):
    id: str
    name: str
    key: dict[str, str]
    pattern: list[str]

class HatDefinition(JsonFileBase[Hat]):
    scope: ClassVar[NamespaceFileScope] = ("hats",)
    extension: ClassVar[str] = ".json"
    data: ClassVar[FileDeserialize[Hat]] = FileDeserialize()
    model = Hat

def load_hats(ctx: Context):
    """Loads hats from the hat yaml file"""
    ctx.data.extend_namespace.append(HatDefinition)
    yield
    ctx.data[HatDefinition].clear()

def beet_default(ctx: Context):
    """Entry point for beet"""
    if not ctx.data[HatDefinition]:
        LOGGER.error("No hats found.")
        return

    generate_hats(ctx)

def generate_hats(ctx: Context):
    """Generate hats from json files"""
    for resource_location in ctx.data[HatDefinition]:
        hat = ctx.data[HatDefinition][resource_location].data

        # Data stuff
        generate_loot_table(ctx, hat)
        generate_recipe(ctx, hat)
        generate_recipe_unlock(ctx, hat)
        give_all(ctx, hat)

        # Asset stuff
        generate_texture_files(ctx, hat)
        add_translation(ctx, hat)

def generate_loot_table(ctx: Context, hat: Hat):
    """Generate a loot table for a hat"""

    ctx.data[f"villager_vanity:{hat.id}"] = LootTable({
        "pools": [
            {
                "rolls": 1,
                "entries": [
                    {
                        "type": "minecraft:item",
                        "name": "minecraft:poisonous_potato",
                        "functions": [
                            {
                                "function": "minecraft:set_components",
                                "components": {
                                    "minecraft:item_name": {"translate":f"item.villager_vanity.{hat.id}", "fallback":"ERROR: RESOURCE PACK NOT ENABLED"},
                                    "minecraft:item_model": f"villager_vanity:{hat.id}",
                                    "!minecraft:food": {},
                                    "minecraft:equippable": {"slot": "head"},
                                    "minecraft:max_stack_size": 1,
                                    "!minecraft:consumable": {},
                                    "minecraft:custom_data": {"villager_vanity":{"ingredient":{"type":hat.id}}, "smithed":{"ignore":{"functionality":True, "crafting":False}}},
                                    "minecraft:lore": [{"translate":"villager_vanity.tooltip","font":"villager_vanity:tooltip","color":"white","italic":False}]
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    })

def generate_recipe(ctx: Context, hat: Hat):
    """Generate a recipe for a hat"""

    ctx.data[f"villager_vanity:{hat.id}"] = Recipe({
        "type": "minecraft:crafting_shaped",
        "category": "equipment",
        "key": hat.key,
        "pattern": hat.pattern,
        "result": {
            "count": 1,
            "id": "minecraft:poisonous_potato",
            "components": {
                "minecraft:item_name": {"translate":f"item.villager_vanity.{hat.id}", "fallback":"ERROR: RESOURCE PACK NOT ENABLED"},
                "minecraft:item_model": f"villager_vanity:{hat.id}",
                "!minecraft:food": {},
                "minecraft:equippable": {"slot": "head"},
                "minecraft:max_stack_size": 1,
                "!minecraft:consumable": {},
                "minecraft:custom_data": {"villager_vanity":{"ingredient":{"type":hat.id}}, "smithed":{"ignore":{"functionality":True, "crafting":False}}},
                "minecraft:lore": [{"translate":"villager_vanity.tooltip","font":"villager_vanity:tooltip","color":"white","italic":False}]
            }
        }
    })

def generate_recipe_unlock(ctx: Context, hat: Hat):
    """Unlocks recipe when an ingredient is picked up"""
    pass
    # custom_data = {"cnk":{"ingredient":{"type":recipe.id}}}
    # if recipe.loot_table:
    #     custom_data = get_custom_data(ctx, recipe.loot_table)
    #     if custom_data is None:
    #         return

    # advancement = ctx.data.advancements["minecraft:recipes/root"].data
    # advancement["criteria"][f"cnk:{recipe.id}"] = {
    #     "trigger": "minecraft:inventory_changed",
    #     "conditions": {
    #         "items": [
    #         {
    #             "items": "minecraft:poisonous_potato",
    #             "predicates": {
    #             "minecraft:custom_data": custom_data
    #             }
    #         }
    #         ]
    #     }
    # }
    # ctx.data[f"villager_vanity:recipes/equipment/{hat.id}"] = Advancement(advancement)

def give_all(ctx: Context, hat: Hat):
    """Generate the give all function"""
    give_function = []
    
    give_function = ctx.data.functions["villager_vanity:give_all"].lines
    give_function.append(f"loot give @s loot villager_vanity:{hat.id}")
    ctx.data["villager_vanity:give_all"] = Function(give_function)

def generate_texture_files(ctx: Context, hat: Hat):
    """Generate texture files for a recipe including item model and item definition"""
    ctx.assets[f"villager_vanity:{hat.id}"] = ItemModel({
        "model": {
            "type": "minecraft:select",
            "property": "minecraft:display_context",
            "cases": [
            {
                "when": [
                "head"
                ],
                "model": {
                "type": "minecraft:model",
                "model": f"villager_vanity:item/{hat.id}"
                }
            }
            ],
            "fallback": {
            "type": "minecraft:model",
            "model": f"villager_vanity:item/{hat.id}_item"
            }
        }
    })

    ctx.assets[f"villager_vanity:item/{hat.id}_item"] = Model({
        "parent": "minecraft:item/generated",
        "textures": {
            "layer0": f"villager_vanity:item/{hat.id}_item"
        }
    })

def add_translation(ctx: Context, hat: Hat):
    """Adds the translation key for a given recipe"""
    lang = ctx.assets.languages["villager_vanity:en_us"].data
    lang[f"item.villager_vanity.{hat.id}"] = hat.name
    ctx.assets["villager_vanity:en_us"] = Language(lang)