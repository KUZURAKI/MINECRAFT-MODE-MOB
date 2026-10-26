package dev.zedkodex.modemob.client;

import dev.zedkodex.modemob.ModeMob;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

@EventBusSubscriber(modid = ModeMob.MODID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public class ClientModEvents {
    @SubscribeEvent
    static void onRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModeMob.TARANTULA.get(), TarantulaRenderer::new);
        event.registerEntityRenderer(ModeMob.WEB_SHOT.get(), ThrownItemRenderer::new);
    }
}
