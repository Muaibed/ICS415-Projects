package com.minecraft.test;

import com.minecraft.core.*;
import com.minecraft.core.entity.Entity;
import com.minecraft.core.entity.Model;
import com.minecraft.core.entity.Texture;
import com.minecraft.core.utils.Consts;
import org.joml.Matrix4f;
import org.joml.Vector2f;
import org.joml.Vector3f;
import org.joml.Vector4f;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.opengl.GL11;

public class TestGame implements ILogic {

    private static final float CAMERA_MOVE_SPEED = 0.005f;

    private final RenderManager renderer;
    private final ObjectLoader loader;
    private final WindowManager window;

    private Entity entity;
    private Camera camera;

    Vector3f cameraInc;
    public TestGame() {
        renderer = new RenderManager();
        window = Launcher.getWindow();
        loader = new ObjectLoader();
        camera = new Camera();
        cameraInc = new Vector3f(0,0,0);
    }

    @Override
    public void init() throws Exception {
        renderer.init();

        float[] vertices = new float[] {
                -0.5f, 0.5f, 0.5f,
                -0.5f, -0.5f, 0.5f,
                0.5f, -0.5f, 0.5f,
                0.5f, 0.5f, 0.5f,
                -0.5f, 0.5f, -0.5f,
                0.5f, 0.5f, -0.5f,
                -0.5f, -0.5f, -0.5f,
                0.5f, -0.5f, -0.5f,
                -0.5f, 0.5f, -0.5f,
                0.5f, 0.5f, -0.5f,
                -0.5f, 0.5f, 0.5f,
                0.5f, 0.5f, 0.5f,
                0.5f, 0.5f, 0.5f,
                0.5f, -0.5f, 0.5f,
                -0.5f, 0.5f, 0.5f,
                -0.5f, -0.5f, 0.5f,
                -0.5f, -0.5f, -0.5f,
                0.5f, -0.5f, -0.5f,
                -0.5f, -0.5f, 0.5f,
                0.5f, -0.5f, 0.5f,
        };
        float[] textCoords = new float[]{
                0.0f, 0.0f,
                0.0f, 0.5f,
                0.5f, 0.5f,
                0.5f, 0.0f,
                0.0f, 0.0f,
                0.5f, 0.0f,
                0.0f, 0.5f,
                0.5f, 0.5f,
                0.0f, 0.5f,
                0.5f, 0.5f,
                0.0f, 1.0f,
                0.5f, 1.0f,
                0.0f, 0.0f,
                0.0f, 0.5f,
                0.5f, 0.0f,
                0.5f, 0.5f,
                0.5f, 0.0f,
                1.0f, 0.0f,
                0.5f, 0.5f,
                1.0f, 0.5f,
        };
        int[] indices = new int[]{
                0, 1, 3, 3, 1, 2,
                8, 10, 11, 9, 8, 11,
                12, 13, 7, 5, 12, 7,
                14, 15, 6, 4, 14, 6,
                16, 18, 19, 17, 16, 19,
                4, 6, 7, 5, 4, 7,
        };

        Model model = loader.loadModel(vertices, textCoords, indices);
        model.setTexture(new Texture(loader.loadTexture("textures/grassblock.png")));
        entity = new Entity(model, new Vector3f(0,0,-5), new Vector3f(0,0,0), 0);

//        GLFW.glfwSetMouseButtonCallback(Launcher.getWindow().getWindow(), (windowHandle, button, action, mods) -> {
//            if (button == GLFW.GLFW_MOUSE_BUTTON_LEFT && action == GLFW.GLFW_PRESS) {
//                // Create new entity at this position
////                Entity newBlock = new Entity(model, new Vector3f(0,3,-5), new Vector3f(0,0,0), 1);
//                entity.setScale(1);
//            }
//        });
    }

    @Override
    public void input() {
        cameraInc.set(0,0,0);
        if (window.isKeyPressed(GLFW.GLFW_KEY_W))
            cameraInc.z = -1;
        if (window.isKeyPressed(GLFW.GLFW_KEY_S))
            cameraInc.z = 1;

        if (window.isKeyPressed(GLFW.GLFW_KEY_A))
            cameraInc.x = -1;
        if (window.isKeyPressed(GLFW.GLFW_KEY_D))
            cameraInc.x = 1;

        if (window.isKeyPressed(GLFW.GLFW_KEY_Z))
            cameraInc.y = -1;
        if (window.isKeyPressed(GLFW.GLFW_KEY_X))
            cameraInc.y= 1;
    }

    @Override
    public void update(float interval, MouseInput mouseInput) {
        camera.movePosition(cameraInc.x * Consts.CAMERA_STEP,
                cameraInc.y * Consts.CAMERA_STEP,
                cameraInc.z * Consts.CAMERA_STEP);

        if (mouseInput.isRightButtonPress()) {
            entity.setScale(0);
            Vector2f rotVec = mouseInput.getDisplVec();
            camera.moveRotation(rotVec.x * Consts.MOUSE_SENSETIVITY, rotVec.y * Consts.MOUSE_SENSETIVITY, 0);
        }

        if (mouseInput.isLeftButtonPress()) {
            entity.setScale(1);
        }

//        entity.incRotation(0.0f, 0.5f, 0.0f);
    }

    @Override
    public void render() {
        if (window.isResize()) {
            GL11.glViewport(0, 0, window.getWidth(), window.getHeight());
            window.setResize(true);
        }

        window.setClearColor(0.0f, 0.0f, 0.0f, 0.0f);
        renderer.render(entity, camera);
    }

    @Override
    public void cleanup() {
        renderer.cleanup();
        loader.cleanup();
    }
}
