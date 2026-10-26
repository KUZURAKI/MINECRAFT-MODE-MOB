package dev.zedkodex.modemob.entity;

import java.util.EnumSet;

import dev.zedkodex.modemob.Config;
import dev.zedkodex.modemob.ModeMob;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.resources.ResourceLocation;

public class Tarantula extends Monster {
    private static final ResourceLocation SPRINT_ID = ResourceLocation.fromNamespaceAndPath(ModeMob.MODID, "sprint");

    public int shootAnim;

    public Tarantula(EntityType<? extends Tarantula> type, Level level) {
        super(type, level);
        this.xpReward = 80;
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 220.0)
                .add(Attributes.MOVEMENT_SPEED, 0.32)
                .add(Attributes.ATTACK_DAMAGE, 10.0)
                .add(Attributes.FOLLOW_RANGE, 40.0)
                .add(Attributes.ARMOR, 6.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.7)
                .add(Attributes.STEP_HEIGHT, 1.2);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(1, new FloatGoal(this));
        goalSelector.addGoal(2, new WebShotGoal(this));
        goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.5, true));
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 12.0f));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (shootAnim > 0) shootAnim--;
        if (level().isClientSide) return;
        AttributeInstance speed = getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed == null) return;
        LivingEntity t = getTarget();
        boolean chase = t != null && t.isAlive() && distanceToSqr(t) < 28 * 28 && hasLineOfSight(t);
        boolean has = speed.getModifier(SPRINT_ID) != null;
        if (chase && !has) speed.addTransientModifier(new AttributeModifier(SPRINT_ID, 0.16, AttributeModifier.Operation.ADD_VALUE));
        else if (!chase && has) speed.removeModifier(SPRINT_ID);
    }

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType spawnType, SpawnGroupData data) {
        SpawnGroupData result = super.finalizeSpawn(level, difficulty, spawnType, data);
        {
            ServerLevel sl = level.getLevel();
            RandomSource r = random;
            int spiders = 8 + r.nextInt(8);
            for (int i = 0; i < spiders; i++) {
                BlockPos p = blockPosition().offset(r.nextInt(15) - 7, 0, r.nextInt(15) - 7);
                p = sl.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p);
                var type = r.nextInt(4) == 0 ? EntityType.CAVE_SPIDER : EntityType.SPIDER;
                var e = type.spawn(sl, p, MobSpawnType.MOB_SUMMONED);
                if (e != null) e.setTarget(null);
            }
            int webs = 40 + r.nextInt(30);
            for (int i = 0; i < webs; i++) {
                BlockPos p = blockPosition().offset(r.nextInt(21) - 10, r.nextInt(4), r.nextInt(21) - 10);
                if (sl.getBlockState(p).isAir() && hasSupport(sl, p)) sl.setBlock(p, Blocks.COBWEB.defaultBlockState(), 2);
            }
        }
        return result;
    }

    private static boolean hasSupport(LevelAccessor level, BlockPos pos) {
        for (Direction d : Direction.values()) {
            BlockState s = level.getBlockState(pos.relative(d));
            if (!s.isAir() && !s.is(Blocks.COBWEB)) return true;
        }
        return false;
    }

    public static boolean checkSpawn(EntityType<Tarantula> type, net.minecraft.world.level.ServerLevelAccessor level, MobSpawnType spawn,
                                     BlockPos pos, RandomSource random) {
        return Monster.checkMonsterSpawnRules(type, level, spawn, pos, random) && random.nextInt(Config.COMMON.tarantulaSpawnRarity.get()) == 0;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return SoundEvents.SPIDER_AMBIENT;
    }

    @Override
    protected SoundEvent getHurtSound(net.minecraft.world.damagesource.DamageSource source) {
        return SoundEvents.SPIDER_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.SPIDER_DEATH;
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        playSound(SoundEvents.SPIDER_STEP, 0.6f, 0.7f);
    }

    @Override
    public boolean canBeLeashed() {
        return false;
    }

    @Override
    public boolean isPersistenceRequired() {
        return false;
    }

    private static class WebShotGoal extends Goal {
        private final Tarantula mob;
        private int cooldown = 40;

        WebShotGoal(Tarantula mob) {
            this.mob = mob;
            setFlags(EnumSet.of(Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity t = mob.getTarget();
            if (t == null || !t.isAlive()) return false;
            double d = mob.distanceToSqr(t);
            return d > 36 && d < 26 * 26 && mob.hasLineOfSight(t);
        }

        @Override
        public boolean canContinueToUse() {
            return canUse();
        }

        @Override
        public void tick() {
            LivingEntity t = mob.getTarget();
            if (t == null) return;
            mob.getLookControl().setLookAt(t, 30f, 30f);
            if (--cooldown > 0) return;
            cooldown = 60 + mob.random.nextInt(50);
            WebShot web = ModeMob.WEB_SHOT.get().create(mob.level());
            if (web == null) return;
            web.setOwner(mob);
            web.setPos(mob.getX(), mob.getY() + 1.2, mob.getZ());
            double dx = t.getX() - mob.getX();
            double dy = t.getEyeY() - web.getY();
            double dz = t.getZ() - mob.getZ();
            web.shoot(dx, dy + Math.sqrt(dx * dx + dz * dz) * 0.1, dz, 1.6f, 1.0f);
            mob.level().addFreshEntity(web);
            mob.shootAnim = 30;
            mob.level().playSound(null, mob.blockPosition(), SoundEvents.SPIDER_AMBIENT, SoundSource.HOSTILE, 1.4f, 0.5f);
        }
    }
}
