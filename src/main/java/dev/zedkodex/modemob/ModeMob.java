package dev.zedkodex.modemob;

import java.util.function.Supplier;

import dev.zedkodex.modemob.entity.Tarantula;
import dev.zedkodex.modemob.entity.WebShot;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.neoforge.common.DeferredSpawnEggItem;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.RegisterSpawnPlacementsEvent;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

@Mod(ModeMob.MODID)
public class ModeMob {
    public static final String MODID = "modemob";

    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(MODID);
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(Registries.ENTITY_TYPE, MODID);

    public static final Supplier<EntityType<Tarantula>> TARANTULA = ENTITIES.register("tarantula",
            () -> EntityType.Builder.<Tarantula>of(Tarantula::new, MobCategory.MONSTER)
                    .sized(2.8F, 1.6F).clientTrackingRange(10).build("tarantula"));
    public static final Supplier<EntityType<WebShot>> WEB_SHOT = ENTITIES.register("web_shot",
            () -> EntityType.Builder.<WebShot>of(WebShot::new, MobCategory.MISC)
                    .sized(0.4F, 0.4F).clientTrackingRange(8).updateInterval(2).build("web_shot"));

    public static final DeferredItem<Item> TARANTULA_EGG = ITEMS.register("tarantula_spawn_egg",
            () -> new DeferredSpawnEggItem(TARANTULA, 0x2A2220, 0xB02020, new Item.Properties()));

    public ModeMob(IEventBus bus, ModContainer container) {
        ITEMS.register(bus);
        ENTITIES.register(bus);
        bus.addListener(ModeMob::attributes);
        bus.addListener(ModeMob::spawnPlacements);
        bus.addListener(ModeMob::tabs);
        container.registerConfig(ModConfig.Type.COMMON, Config.COMMON_SPEC);
    }

    private static void attributes(EntityAttributeCreationEvent event) {
        event.put(TARANTULA.get(), Tarantula.attributes().build());
    }

    private static void spawnPlacements(RegisterSpawnPlacementsEvent event) {
        event.register(TARANTULA.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Tarantula::checkSpawn, RegisterSpawnPlacementsEvent.Operation.OR);
    }

    private static void tabs(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.SPAWN_EGGS) event.accept(TARANTULA_EGG.get());
    }
}
