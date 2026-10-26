package dev.zedkodex.modemob.client;

import java.io.Reader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import dev.zedkodex.modemob.ModeMob;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

public final class RigMesh {
    private static final class Node {
        String name;
        int parent;
        float[] t = new float[3];
        float[] r = new float[4];
        float[] s = new float[3];
        float[] m;
        float[] v;
    }

    private static final class Channel {
        int node;
        char path;
        float[] times;
        float[] vals;
    }

    private static final class Anim {
        float len;
        List<Channel> channels = new ArrayList<>();
    }

    private static final Map<String, RigMesh> CACHE = new HashMap<>();

    public final ResourceLocation texture;
    private final List<Node> nodes = new ArrayList<>();
    private final Map<String, Anim> anims = new HashMap<>();
    private final float scale;
    private final float[] origin;

    private final Matrix4f[] world;
    private final boolean[] done;
    private final Vector3f[] tr;
    private final Quaternionf[] rot;
    private final Vector3f[] sc;
    private final Vector3f tmp = new Vector3f();
    private final Vector3f p0 = new Vector3f();
    private final Vector3f p1 = new Vector3f();
    private final Vector3f p2 = new Vector3f();

    public static RigMesh get(String name) {
        return CACHE.computeIfAbsent(name, RigMesh::new);
    }

    public static void clear() {
        CACHE.clear();
    }

    private static float[] floats(JsonArray a) {
        float[] f = new float[a.size()];
        for (int i = 0; i < f.length; i++) f[i] = a.get(i).getAsFloat();
        return f;
    }

    private RigMesh(String name) {
        texture = ResourceLocation.fromNamespaceAndPath(ModeMob.MODID, "textures/entity/" + name + ".png");
        ResourceLocation data = ResourceLocation.fromNamespaceAndPath(ModeMob.MODID, "geo/" + name + ".json");
        try (Reader rd = Minecraft.getInstance().getResourceManager().getResourceOrThrow(data).openAsReader()) {
            JsonObject json = JsonParser.parseReader(rd).getAsJsonObject();
            scale = json.get("scale").getAsFloat();
            origin = floats(json.getAsJsonArray("origin"));
            for (JsonElement e : json.getAsJsonArray("nodes")) {
                JsonObject o = e.getAsJsonObject();
                Node n = new Node();
                n.name = o.get("name").getAsString();
                n.parent = o.get("parent").getAsInt();
                n.t = floats(o.getAsJsonArray("t"));
                n.r = floats(o.getAsJsonArray("r"));
                n.s = floats(o.getAsJsonArray("s"));
                if (o.has("m")) n.m = floats(o.getAsJsonArray("m"));
                if (o.has("v")) n.v = floats(o.getAsJsonArray("v"));
                nodes.add(n);
            }
            JsonObject an = json.getAsJsonObject("anims");
            for (String key : an.keySet()) {
                JsonObject a = an.getAsJsonObject(key);
                Anim anim = new Anim();
                anim.len = a.get("len").getAsFloat();
                for (JsonElement ce : a.getAsJsonArray("ch")) {
                    JsonObject c = ce.getAsJsonObject();
                    Channel ch = new Channel();
                    ch.node = c.get("node").getAsInt();
                    ch.path = c.get("path").getAsString().charAt(0);
                    ch.times = floats(c.getAsJsonArray("times"));
                    ch.vals = floats(c.getAsJsonArray("vals"));
                    anim.channels.add(ch);
                }
                anims.put(key, anim);
            }
        } catch (Exception ex) {
            throw new IllegalStateException("Cannot load " + data, ex);
        }
        int n = nodes.size();
        world = new Matrix4f[n];
        done = new boolean[n];
        tr = new Vector3f[n];
        rot = new Quaternionf[n];
        sc = new Vector3f[n];
        for (int i = 0; i < n; i++) {
            world[i] = new Matrix4f();
            tr[i] = new Vector3f();
            rot[i] = new Quaternionf();
            sc[i] = new Vector3f();
        }
    }

    public float length(String anim) {
        Anim a = anims.get(anim);
        return a == null ? 1f : a.len;
    }

    private void sample(Anim a, float time) {
        float t = a.len > 0 ? time % a.len : 0;
        for (Channel ch : a.channels) {
            float[] times = ch.times;
            int k = 0;
            while (k < times.length - 2 && times[k + 1] <= t) k++;
            float t0 = times[k];
            float t1 = times[Math.min(k + 1, times.length - 1)];
            float f = t1 > t0 ? Math.min(1f, Math.max(0f, (t - t0) / (t1 - t0))) : 0f;
            int k1 = Math.min(k + 1, times.length - 1);
            switch (ch.path) {
                case 't' -> tr[ch.node].set(ch.vals[k * 3], ch.vals[k * 3 + 1], ch.vals[k * 3 + 2])
                        .lerp(tmp.set(ch.vals[k1 * 3], ch.vals[k1 * 3 + 1], ch.vals[k1 * 3 + 2]), f);
                case 's' -> sc[ch.node].set(ch.vals[k * 3], ch.vals[k * 3 + 1], ch.vals[k * 3 + 2])
                        .lerp(tmp.set(ch.vals[k1 * 3], ch.vals[k1 * 3 + 1], ch.vals[k1 * 3 + 2]), f);
                default -> rot[ch.node].set(ch.vals[k * 4], ch.vals[k * 4 + 1], ch.vals[k * 4 + 2], ch.vals[k * 4 + 3])
                        .slerp(new Quaternionf(ch.vals[k1 * 4], ch.vals[k1 * 4 + 1], ch.vals[k1 * 4 + 2], ch.vals[k1 * 4 + 3]), f);
            }
        }
    }

    private Matrix4f resolve(int i) {
        if (done[i]) return world[i];
        Node n = nodes.get(i);
        Matrix4f local = new Matrix4f();
        if (n.m != null && tr[i].equals(n.t[0], n.t[1], n.t[2]) && rot[i].equals(new Quaternionf(n.r[0], n.r[1], n.r[2], n.r[3]), 1e-6f)) {
            local.set(n.m[0], n.m[1], n.m[2], n.m[3], n.m[4], n.m[5], n.m[6], n.m[7], n.m[8], n.m[9], n.m[10], n.m[11], n.m[12], n.m[13], n.m[14], n.m[15]);
        } else {
            local.translationRotateScale(tr[i], rot[i], sc[i]);
        }
        if (n.parent >= 0) world[i].set(resolve(n.parent)).mul(local);
        else world[i].set(local);
        done[i] = true;
        return world[i];
    }

    public void render(PoseStack pose, VertexConsumer vc, int light, String anim, float time) {
        for (int i = 0; i < nodes.size(); i++) {
            Node n = nodes.get(i);
            tr[i].set(n.t[0], n.t[1], n.t[2]);
            rot[i].set(n.r[0], n.r[1], n.r[2], n.r[3]);
            sc[i].set(n.s[0], n.s[1], n.s[2]);
            done[i] = false;
        }
        Anim a = anims.get(anim);
        if (a != null) sample(a, time);

        pose.pushPose();
        pose.scale(scale, scale, scale);
        pose.translate(-origin[0], -origin[1], -origin[2]);
        PoseStack.Pose last = pose.last();
        Matrix4f pm = new Matrix4f(last.pose());
        for (int i = 0; i < nodes.size(); i++) {
            Node n = nodes.get(i);
            if (n.v == null) continue;
            Matrix4f w = resolve(i);
            float[] v = n.v;
            for (int t = 0; t < v.length / 15; t++) {
                int o = t * 15;
                w.transformPosition(v[o], v[o + 1], v[o + 2], p0);
                w.transformPosition(v[o + 5], v[o + 6], v[o + 7], p1);
                w.transformPosition(v[o + 10], v[o + 11], v[o + 12], p2);
                Vector3f nrm = new Vector3f(p1).sub(p0).cross(new Vector3f(p2).sub(p0));
                if (nrm.lengthSquared() > 1e-12f) nrm.normalize();
                for (int k = 0; k < 4; k++) {
                    Vector3f p = k == 0 ? p0 : k == 1 ? p1 : p2;
                    int i2 = o + Math.min(k, 2) * 5;
                    vc.addVertex(last, p.x, p.y, p.z)
                            .setColor(0xFFFFFFFF)
                            .setUv(v[i2 + 3], v[i2 + 4])
                            .setOverlay(OverlayTexture.NO_OVERLAY)
                            .setLight(light)
                            .setNormal(last, nrm.x, nrm.y, nrm.z);
                }
            }
        }
        pose.popPose();
    }
}
