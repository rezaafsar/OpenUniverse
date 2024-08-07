import threading
from Engine2.Screen import *
from Engine2.LoadObject import *
from Engine2.Light import *
from Engine2.Material import *
from Engine2.Axes import *
from Engine2.CellAttach import *
from Level.ObjectAttach import *
from Engine2.Cullings.DistanceCulling import *
from Level.Shematic import *
from Level.Chunk import *
from Level.ManualChunkGen import *
from time import sleep
from datetime import datetime
from time import time


class MultiShaders(Screen):

    def __init__(self):
        if ESP:
            print("Starting Engine...")
        else:
            print("ESP (ENGINE_STATUS_PRINT) IS OFF!")
        print("Project repo: https://github.com/MatinAfzal/OpenUniverse")

        start = datetime.now()
        print("Starting at:" + str(start.now()))

        super().__init__(SCREEN_POS_X, SCREEN_POS_Y, SCREEN_WIDTH, SCREEN_HEIGHT)

        self.plane = None
        self.cube = None
        self.light = None
        self.axes = None
        self.obj_cube = None
        self.img_cube = None
        self.mat = None
        self.seed = 0

        # Class init
        self.culling_distance = DistanceCulling(distance=DCD)
        # self.shematic = Shematic(1)

        # Switching draw types
        self.draw_types = [GL_POINTS, GL_LINES, GL_TRIANGLES]
        self.v_counter = 0

        # Switching Cull Face
        self.c_counter = 0

        # Switching World axes status
        self.x_counter = 1

        # Moving sun
        self.s_counter = 1

        # img
        self.img_texture = r"Textures\texture.png"
        self.img_icu = r"Textures\ICU.png"
        self.img_sun = r"Textures\sun.jpeg"
        self.img_cactus = r"Textures\cactus.png"

        # Loads
        if ESP:
            print("Loading Files...")

        # objects
        self.obj_cube = r"Models\cube.obj"
        self.obj_donut = r"Models\donut.obj"

        # Shaders
        texturevert = r"Shaders/texturedvert.vs"
        texturefrag = r"Shaders/texturedfrag.vs"
        vertexcolvert = r"Shaders/vertexcolvert.vs"
        vertexcolfrag = r"Shaders/vertexcolfrag.vs"

        # Shaders
        if ESP:
            print("Loading Shaders...")
        self.mat = Material(texturevert, texturefrag)
        axesmat = Material(vertexcolvert, vertexcolfrag)

        # Entity
        if ESP:
            print("Loading Entitis...")
        self.axes = Axes(pygame.Vector3(0, 0, 0), axesmat)

        self.light_pos = pygame.Vector3(-80, -60, 110)
        self.initial_light_pos = self.light_pos.copy()
        self.lightbolb_pos = pygame.Vector3(self.light_pos.x, self.light_pos.y + 5, self.light_pos.z)
        self.light = Light(self.light_pos, pygame.Vector3(1, 1, 1), 0)
        self.camera = Camera(self.screen_width, self.screen_height)
        self.camera_pos = self.get_cam_pos()
        self.cube0 = LoadObject(
            self.obj_cube, imagefile=self.img_sun, draw_type=GL_TRIANGLES, material=self.mat,
            location=self.lightbolb_pos, scale=pygame.Vector3(8, 8, 8))
        self.start_time = int(time())

        # Object Attach
        self.trees = None
        self.terrain = None

        self.threading()

        # self.terrain = ObjectAttach(object_name="chunk", object_type="desert", number_x=10, number_z=10)
        # self.trees = ObjectAttach(object_name="cactus", number_x=10, number_z=10)

        # Cell Attaches
        cell_start = datetime.now()
        if ESP:
            print("Cell Attach started at:" + str(cell_start.now()))

        self.forest = CellAttach(self.trees.layer, shader=self.mat, image=self.img_texture)
        self.world = CellAttach(self.terrain.layer, shader=self.mat, image=self.img_texture)

        # self.forest = CellAttach(self.trees.layer, shader=self.mat, image=self.img_cactus)
        # self.chunk = Chunk(biome="jungle", position=Vector3(0, 0, 0), img=self.img_texture, material=self.mat)

        # Sky variables
        self.sky_cycle_lock = False
        self.sun_cycle_lock = False
        self.red = 0.0
        self.green = 0.0
        self.blue = 0.0
        self.alpha = 0.5

    def threading(self):
        t1 = threading.Thread(target=self.tree_thread_)
        t2 = threading.Thread(target=self.terrain_thread_)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    def tree_thread_(self):
        self.trees = ObjectAttach(object_name="tree", number_x=TREES, number_z=TREES)

    def terrain_thread_(self):
        self.terrain = ObjectAttach(object_name="chunk", object_type="jungle", number_x=CHUNKS, number_z=CHUNKS)

    def get_cam_pos(self):
        return int(self.camera.transformation[0, 3]), int(self.camera.transformation[2, 3])

    def initialise(self):
        # Variables
        if ESP:
            print("Loading Variables...")

        cell_end = datetime.now()
        if ESP:
            print("Cell Attach ended at:" + str(cell_end.now()))

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def camera_init(self):
        pass

    def display(self):
        # glClearColor(0.5, 0.5 ,0.5, 0.5) # Middle gray
        # glClearColor(0.58, 0.85, 0.94, 0.5)  # Sky blue
        glClearColor(self.red, self.green, self.blue, self.alpha)  # Sky night
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #####
        keys = pygame.key.get_pressed()
        if keys[pygame.K_v]:
            if self.v_counter >= 3:
                self.v_counter = 0
            self.world.world_draw_type = self.draw_types[self.v_counter]
            self.forest.world_draw_type = self.draw_types[self.v_counter]
            if ESP:
                print("Draw Type switched...")
            self.world.load_world()
            self.forest.load_world()
            self.v_counter += 1
            sleep(0.3)

        if keys[pygame.K_c]:
            if self.c_counter > 1:
                self.c_counter = 0

            if self.c_counter == 0:
                if ESP:
                    print("Cull Face enabled...")
                glEnable(GL_CULL_FACE)

            else:
                if ESP:
                    print("Cull Face disabled...")
                glDisable(GL_CULL_FACE)

            self.c_counter += 1
            sleep(0.3)

        if keys[pygame.K_x]:
            self.x_counter += 1
            if self.x_counter > 1:
                self.x_counter = 0

            if self.x_counter == 0:
                if ESP:
                    print("World Center axes enabled...")
            else:
                if ESP:
                    print("World Center axes disabled...")

            sleep(0.3)

        if keys[pygame.K_l]:
            if self.s_counter >= 2:
                self.s_counter = 0
            else:
                self.s_counter += 1

            sleep(0.3)

        # #####################RENDER#######################
        glPointSize(10)
        if self.x_counter == 0:
            self.axes.draw(self.camera, self.light)

        try:
            self.world.world.draw(self.camera, self.light)
            self.forest.world.draw(self.camera, self.light)
        except:
            pass

        self.cube0.draw(self.camera, self.light)

        # #####################RENDER#######################

        now = int(time())
        current_time = self.start_time - now

        if current_time % 1 == 0 and SKY_DYNAMIC:
            if self.green >= 1 and self.blue >= 1:
                self.sky_cycle_lock = True

            if not self.sky_cycle_lock:
                self.red = 0
                self.green += SKY_SPEED
                self.blue += SKY_SPEED

            if self.sky_cycle_lock:
                self.red = 0
                self.green -= SKY_SPEED
                self.blue -= SKY_SPEED

                if self.green <= 0 and self.blue <= 0:
                    self.sky_cycle_lock = False

        if current_time % 1 == 0 and self.s_counter == 1:
            if self.light_pos.y < 120 and self.light_pos.x < 300 and not self.sun_cycle_lock:
                self.light_pos.y += 0.078
            elif self.light_pos.y >= 120 and self.light_pos.x < 300 and not self.sun_cycle_lock:
                self.light_pos.x += 0.138
            elif self.light_pos.y >= 118 and self.light_pos.x >= 298 and not self.sun_cycle_lock:
                self.sun_cycle_lock = True
            elif self.sun_cycle_lock:
                if self.light_pos.y <= -60 and self.sun_cycle_lock:
                    self.light_pos = self.initial_light_pos.copy()
                    self.sun_cycle_lock = False
                else:
                    self.light_pos.y -= 0.078

            self.lightbolb_pos = self.light_pos
            self.cube0 = LoadObject(self.obj_cube, imagefile=self.img_sun, draw_type=GL_TRIANGLES, material=self.mat,
                                    location=self.lightbolb_pos, scale=pygame.Vector3(8, 8, 8))
            self.light.position = pygame.Vector3(self.light_pos.x, self.light_pos.y, self.light_pos.z)
            self.light.update(self.mat.program_id)

        if current_time % 1 == 0 and self.s_counter == 2:
            self.light_pos.x -= 0.1
            self.light_pos.z -= 0.1
            self.lightbolb_pos = self.light_pos

            self.cube0 = LoadObject(self.obj_cube, imagefile=self.img_sun, draw_type=GL_TRIANGLES, material=self.mat,
                                    location=self.lightbolb_pos, scale=pygame.Vector3(8, 8, 8))
            self.light.position = pygame.Vector3(self.light_pos.x, self.light_pos.y, self.light_pos.z)
            self.light.update(self.mat.program_id)


if __name__ == "__main__":
    MultiShaders().mainloop()
    if ESP:
        print("Mainloop Ends...")
    end = datetime.now()
    print("Ended at:" + str(end.now()))
    print("\n\n\n")
