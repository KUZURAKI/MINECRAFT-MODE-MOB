package dev.zedkodex.modemob.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import dev.zedkodex.modemob.entity.Tarantula;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

public class TarantulaRenderer extends EntityRenderer<Tarantula> {
    public TarantulaRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
        shadowRadius = 1.6f;
    }

    @Override
    public void render(Tarantula e, float yaw, float partial, PoseStack pose, MultiBufferSource buffer, int light) {
        RigMesh rig = RigMesh.get("tarantula");
        float speed = e.walkAnimation.speed(partial);
        String anim = "idle";
        float time = (e.tickCount + partial) / 20f;
        if (e.shootAnim > 0 || (e.getTarget() != null && e.isAggressive() && e.distanceToSqr(e.getTarget()) < 25)) {
            anim = "attack";
        } else if (speed > 0.04f) {
            anim = "walk";
            time = e.walkAnimation.position(partial) * rig.length("walk") / 7f;
        }
        pose.pushPose();
        pose.mulPose(Axis.YP.rotationDegrees(180f - Mth.rotLerp(partial, e.yBodyRotO, e.yBodyRot)));
        if (e.deathTime > 0) {
            pose.mulPose(Axis.ZP.rotationDegrees(Math.min(1f, (e.deathTime + partial) / 20f) * 90f));
        }
        rig.render(pose, buffer.getBuffer(RenderType.entityCutoutNoCull(rig.texture)), light, anim, time);
        pose.popPose();
        super.render(e, yaw, partial, pose, buffer, light);
    }

    @Override
    public ResourceLocation getTextureLocation(Tarantula e) {
        return RigMesh.get("tarantula").texture;
    }
}
