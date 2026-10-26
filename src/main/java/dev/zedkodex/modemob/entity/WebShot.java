package dev.zedkodex.modemob.entity;

import dev.zedkodex.modemob.ModeMob;
import net.minecraft.core.BlockPos;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;

public class WebShot extends ThrowableItemProjectile {
    public WebShot(EntityType<? extends WebShot> type, Level level) {
        super(type, level);
    }

    @Override
    protected Item getDefaultItem() {
        return Items.COBWEB;
    }

    @Override
    protected double getDefaultGravity() {
        return 0.03;
    }

    private void web(BlockPos pos) {
        if (level().getBlockState(pos).canBeReplaced() && level().getBlockState(pos).getFluidState().isEmpty()) {
            level().setBlock(pos, Blocks.COBWEB.defaultBlockState(), 3);
        }
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        if (level().isClientSide) return;
        if (result.getEntity() instanceof LivingEntity e && !(e instanceof Tarantula)) {
            e.hurt(damageSources().mobProjectile(this, getOwner() instanceof LivingEntity o ? o : null), 2.0f);
            e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 6, false, true));
            web(e.blockPosition());
            web(e.blockPosition().above());
        }
        discard();
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        super.onHitBlock(result);
        if (level().isClientSide) return;
        web(result.getBlockPos().relative(result.getDirection()));
        discard();
    }
}
