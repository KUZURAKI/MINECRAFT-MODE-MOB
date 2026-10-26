package dev.zedkodex.modemob;

import net.neoforged.neoforge.common.ModConfigSpec;
import org.apache.commons.lang3.tuple.Pair;

public class Config {
    public static final Common COMMON;
    public static final ModConfigSpec COMMON_SPEC;

    static {
        Pair<Common, ModConfigSpec> c = new ModConfigSpec.Builder().configure(Common::new);
        COMMON = c.getLeft();
        COMMON_SPEC = c.getRight();
    }

    public static class Common {
        public final ModConfigSpec.IntValue tarantulaSpawnRarity;

        Common(ModConfigSpec.Builder b) {
            b.push("tarantula");
            tarantulaSpawnRarity = b.comment("Tarantula spawn is allowed once per this many valid spawn attempts, higher is rarer").defineInRange("spawnRarity", 6, 1, 200);
            b.pop();
        }
    }
}
