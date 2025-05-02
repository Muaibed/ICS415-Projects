package com.minecraft.test;

import com.minecraft.core.EngineManager;
import com.minecraft.core.WindowManager;
import com.minecraft.core.utils.Consts;
import org.lwjgl.Version;

public class Launcher {
    private static WindowManager window;
    private static TestGame game;

    public static WindowManager getWindow() {
        return window;
    }

    public static void main(String[] args) {
        window = new WindowManager(Consts.TITLE, 1600, 900, false);
        game = new TestGame();
        EngineManager engine = new EngineManager();

        try {
            engine.start();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static TestGame getGame() {
        return game;
    }
}
