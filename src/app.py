import mysql.connector
import Tkinter as tk
import ttk

from drones import Drone, DroneStore
from operators import Operator, OperatorStore
from maps import Map, MapStore
from trackingsystem import TrackingSystem, DroneLocation


class Application(object):
    """ Main application view - displays the menu. """

    def __init__(self, conn):
        # Initialise the stores
        self.drones = DroneStore(conn)
        self.operators = OperatorStore(conn)
        self.maps = MapStore(conn)
        self.tracker = TrackingSystem()

        # Assign drones to their maps
        for drone in self.drones.list_all():
            if drone.map != None:
                map_name = drone.map
                drone.map = self.maps.get(map_name)
                drone.location = self.tracker.retrieve(drone.map, drone)
            
        # Initialise the GUI window
        self.root = tk.Tk()
        self.root.title('Drone Allocation and Localisation')
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # Add in the buttons
        drone_button = tk.Button(
            frame, text="View Drones", command=self.view_drones, width=40, padx=5, pady=5)
        drone_button.pack(side=tk.TOP)
        operator_button = tk.Button(
            frame, text="View Operators", command=self.view_operators, width=40, padx=5, pady=5)
        operator_button.pack(side=tk.TOP)
        map_button = tk.Button(
            frame, text="View Maps", command=self.view_maps, width=40, padx=5, pady=5)
        map_button.pack(side=tk.TOP)
        allocate_button = tk.Button(
            frame, text="Allocate Drone", command=self.view_drone_allocation, width=40, padx=5, pady=5)
        allocate_button.pack(side=tk.TOP)
        exit_button = tk.Button(frame, text="Exit System",
                                command=quit, width=40, padx=5, pady=5)
        exit_button.pack(side=tk.TOP)

    def main_loop(self):
        """ Main execution loop - start Tkinter. """
        self.root.mainloop()

    def view_operators(self):
        """ Display the operators. """
        wnd = OperatorListWindow(self)
        self.root.wait_window(wnd.root)

    def view_drones(self):
        """ Display the drones. """
        wnd = DroneListWindow(self)
        self.root.wait_window(wnd.root)
    
    def view_maps(self):
        """ Display the maps. """
        wnd = MapWindow(self)
        self.root.wait_window(wnd.root)

    def view_drone_allocation(self):
        """ Display the drone allocation window. """
        wnd = AllocationWindow(self)
        self.root.wait_window(wnd.root)

class AllocationWindow(object):

    def __init__(self, parent):
        # Add a variable to hold the stores
        self.drones = parent.drones
        self.maps = parent.maps
        self.operators = parent.operators

        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title("Allocate Drone")
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

        self.checked = False

        drone_label = tk.Label(self.frame, text="Drone:")
        self.drone_var = tk.StringVar(self.frame)
        options_drones = []
        for drone in self.drones.list_all():
            options_drones.append(drone.name)
        self.drone_var.set(options_drones[0])
        drone_dropdown = tk.OptionMenu(self.frame, self.drone_var, *options_drones)

        operator_label = tk.Label(self.frame, text="Operator:")
        self.operator_var = tk.StringVar(self.frame)
        options_operators = []
        for operator in self.operators.list_all():
            options_operators.append(operator.first_name + ' ' + operator.family_name)
        self.operator_var.set(options_operators[0])
        operator_dropdown = tk.OptionMenu(self.frame, self.operator_var, *options_operators)

        drone_label.grid(in_=self.frame, row=0, column=0, sticky=tk.W)
        drone_dropdown.grid(in_=self.frame, row=0, column=1, sticky=tk.W)
        
        operator_label.grid(in_=self.frame, row=1, column=0, sticky=tk.W)
        operator_dropdown.grid(in_=self.frame, row=1, column=1, sticky=tk.W)

        self.errors_text = tk.Text(self.frame, height=5, width=30)
        self.errors_text.grid(in_=self.frame, row=2, column=0, sticky=tk.EW)

        # Check button
        check_button = tk.Button(self.frame, text="Check",
                                command=self.check, width=20, padx=5, pady=5)
        check_button.grid(in_=self.frame, row=3, column=1, sticky=tk.E)

        # Allocate button
        allocate_button = tk.Button(self.frame, text="Allocate",
                                command=self.allocate, width=20, padx=5, pady=5)
        allocate_button.grid(in_=self.frame, row=4, column=1, sticky=tk.E)

        # Exit button
        exit_button = tk.Button(self.frame, text="Cancel",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=5, column=1, sticky=tk.E)
    
    def check(self):
        self.checked = True
        self.errors_text.delete('1.0', tk.END)
        drone_to_allocate = None
        operator_to_allocate = None
        for drone in self.drones.list_all():
            if drone.name == self.drone_var.get():
                drone_to_allocate = drone
        for operator in self.operators.list_all():
            if operator.first_name + ' ' + operator.family_name == self.operator_var.get():
                operator_to_allocate = operator

        self.action = self.drones.allocate(drone_to_allocate, operator_to_allocate)
        for message in self.action.messages:
            self.errors_text.insert(tk.END, message+'\n')
        
        if self.action.messages == []:
            self.errors_text.insert(tk.END, "No Errors")

    def allocate(self):
        if not self.checked:
            self.errors_text.insert(tk.END, "The allocation has not been checked.\n")
        else:
            operator = self.action.commit()
            self.operators.save(operator)
        self.root.destroy()

    def close(self):
        """ Closes the list window. """
        self.root.destroy()

class MapWindow(object):
    """ Map viewer window. """

    def __init__(self, parent):
        # Add a variable to hold the stores
        self.drones = parent.drones
        self.maps = parent.maps

        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title("Map Viewer")
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

        self.draw_map()
        self.draw_drones()
        
        # Exit button
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=5, column=0, sticky=tk.E)

        # Refesh Butotn
        refresh_button = tk.Button(self.frame, text="Refresh",
                                   command=self.refresh_drones, width=20, padx=5, pady=5)
        refresh_button.grid(in_=self.frame, row=4, column=0, sticky=tk.E)

    def draw_drones(self):
        spacing_y = self.img.width() / 100
        spacing_x = self.img.height() / 100
        self.current_drones = []
        for drone in self.drones.list_all():
            if drone.map.name == self.map_var.get():
                drone.location.is_valid()
                x1 = drone.location.position()[0] * spacing_y
                x2 = x1 + 15
                y1 = drone.location.position()[1] * spacing_x
                y2 = y1 + 15
            
                if drone.rescue == 1:
                    self.current_drones.append(self.canvas.create_oval(x1, y1, x2, y2, fill='blue'))
                else:
                    self.current_drones.append(self.canvas.create_oval(x1, y1, x2, y2, fill='red'))

    def refresh_drones(self):
        for i in self.current_drones:
            self.canvas.delete(i)

        spacing_y = self.img.width() / 100
        spacing_x = self.img.height() / 100

        for drone in self.drones.list_all():
            if drone.map.name == self.map_var.get():
                drone.location.is_valid()
                x1 = drone.location.position()[0] * spacing_y
                x2 = x1 + 15
                y1 = drone.location.position()[1] * spacing_x
                y2 = y1 + 15
                if drone.rescue == 1:
                    self.current_drones.append(self.canvas.create_oval(x1, y1, x2, y2, fill='blue'))
                else:
                    self.current_drones.append(self.canvas.create_oval(x1, y1, x2, y2, fill='red'))

    def change_map(self, *args):
        self.img = tk.PhotoImage(file=self.maps.get(self.map_var.get()).filepath)
        self.canvas.create_image(0, 0, image=self.img, anchor=tk.NW)
        self.canvas.config(scrollregion=(0,0,self.img.width(),self.img.height()))
        self.draw_drones()
    
    def draw_map(self):
        self.img = None
        map_names = []

        for map_ in self.maps.list_all():
            map_names.append(map_.name)

        self.map_var = tk.StringVar(self.frame)
        self.map_var.set(map_names[0])
        self.map_var.trace("w", self.change_map)
        map_option = tk.OptionMenu(self.frame, self.map_var, *map_names)

        self.img = tk.PhotoImage(file=self.maps.get(map_names[0]).filepath)

        self.canvas = tk.Canvas(self.frame, width=800, height=500, bg='black', scrollregion=(0,0,self.img.width(),self.img.height()))

        hbar=tk.Scrollbar(self.frame,orient=tk.HORIZONTAL)
        hbar.grid(in_=self.frame,row=3,column=0,sticky=tk.EW)
        hbar.config(command=self.canvas.xview)

        vbar=tk.Scrollbar(self.frame,orient=tk.VERTICAL)
        vbar.grid(in_=self.frame,row=2,column=1,sticky=tk.NS)
        vbar.config(command=self.canvas.yview)
        
        self.canvas.config(width=800,height=500)
        self.canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        self.canvas.grid(in_=self.frame, row=2, column=0, sticky=tk.W)
        map_option.grid(in_=self.frame, row=1, column=0, sticky=tk.W)

        self.canvas.create_image(0, 0, image=self.img, anchor=tk.NW)
    
    def close(self):
        """ Closes the list window. """
        self.root.destroy()

class ListWindow(object):
    """ Base list window. """

    def __init__(self, parent, title):
        # Add a variable to hold the stores
        self.drones = parent.drones
        self.operators = parent.operators

        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

    def add_list(self, columns, edit_action):
        # Add the list
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.title())
        ysb = ttk.Scrollbar(self.frame, orient=tk.VERTICAL,
                            command=self.tree.yview)
        xsb = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL,
                            command=self.tree.xview)
        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set
        self.tree.bind("<Double-1>", edit_action)

        # Add tree and scrollbars to frame
        self.tree.grid(in_=self.frame, row=0, column=0, sticky=tk.NSEW)
        ysb.grid(in_=self.frame, row=0, column=1, sticky=tk.NS)
        xsb.grid(in_=self.frame, row=1, column=0, sticky=tk.EW)

        # Set frame resize priorities
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

    def close(self):
        """ Closes the list window. """
        self.root.destroy()


class DroneListWindow(ListWindow):
    """ Window to display a list of drones. """

    def __init__(self, parent):
        super(DroneListWindow, self).__init__(parent, 'Drones')

        # Add the list and fill it with data
        columns = ('id', 'name', 'class', 'rescue', 'operator')
        self.add_list(columns, self.edit_drone)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Drone",
                               command=self.add_drone, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        self.tree.delete(*self.tree.get_children())
        for drone in self.drones.list_all():
            self.tree.insert('', 'end', values=(drone.id, 
                                                drone.name, 
                                                drone.class_type, 
                                                drone.rescue, 
                                                drone.operator))

    def add_drone(self):
        """ Starts a new drone and displays it in the list. """
        # Start a new drone instance
        drone = Drone('')

        # Display the drone
        self.view_drone(drone, self._save_new_drone)

    def _save_new_drone(self, drone):
        """ Saves the drone in the store and updates the list. """
        self.drones.add(drone)
        self.populate_data()

    def edit_drone(self, event):
        """ Retrieves the drone and shows it in the editor. """
        # Retrieve the identifer of the drone
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][0]

        # Load the drone from the store
        drone = self.drones.get(item_id)

        # Display the drone
        self.view_drone(drone, self._update_drone)

    def _update_drone(self, drone):
        """ Saves the new details of the drone. """
        self.drones.save(drone)
        self.populate_data()

    def view_drone(self, drone, save_action):
        """ Displays the drone editor. """
        wnd = DroneEditorWindow(self, drone, save_action)
        self.root.wait_window(wnd.root)

class OperatorListWindow(ListWindow):
    """ Window to display a list of operators. """

    def __init__(self, parent):
        super(OperatorListWindow, self).__init__(parent, 'Operators')

        # Add the list and fill it with data
        columns = ('name', 'class', 'rescue', 'operations', 'drone')
        self.add_list(columns, self.edit_operator)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Operator",
                               command=self.add_operator, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        self.tree.delete(*self.tree.get_children())
        for operator in self.operators.list_all():
            if operator.drone == None:
                operator_drone = "<None>"
            else:
                operator_drone = str(operator.drone) + ". " + self.drones.get(operator.drone).name
            if operator.drone_license == 1:
                operator_drone_license = "One"
            else:
                operator_drone_license = "Two"
            if operator.rescue_endorsement == 1:
                operator_rescue_endorsement = "Yes"
            else:
                operator_rescue_endorsement = "No"
            self.tree.insert('', 'end', values=(operator.first_name + ' ' + operator.family_name, 
                                                operator_drone_license, 
                                                operator_rescue_endorsement, 
                                                operator.operations, 
                                                operator_drone))

    def add_operator(self):
        """ Starts a new operator and displays it in the list. """
        # Start a new operator instance
        operator = Operator()

        # Display the operator
        self.view_operator(operator, self._save_new_operator)

    def _save_new_operator(self, operator):
        """ Saves the drone in the store and updates the list. """
        self.operators._add(operator)
        self.populate_data()

    def edit_operator(self, event):
        """ Retrieves the drone and shows it in the editor. """
        # Retrieve the identifer of the operator
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][0]

        # Load the operator from the store
        operator = self.operators.get(item_id)

        # Display the operator
        self.view_operator(operator, self._update_operator)

    def _update_operator(self, operator):
        """ Saves the new details of the operator. """
        self.operators.save(operator)
        self.populate_data()

    def view_operator(self, operator, save_action):
        """ Displays the operator editor. """
        wnd = OperatorEditorWindow(self, operator, save_action)
        self.root.wait_window(wnd.root)

class EditorWindow(object):
    """ Base editor window. """

    def __init__(self, parent, title, save_action):
        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

        # Add the editor widgets
        last_row = self.add_editor_widgets()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Save",
                               command=save_action, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=last_row + 1, column=3, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=last_row + 2, column=3, sticky=tk.E)

    def add_editor_widgets(self):
        """ Adds the editor widgets to the frame - this needs to be overriden in inherited classes. 
        This function should return the row number of the last row added - EditorWindow uses this
        to correctly display the buttons. """
        return -1

    def close(self):
        """ Closes the editor window. """
        self.root.destroy()

class DroneEditorWindow(EditorWindow):
    """ Editor window for drones. """

    def __init__(self, parent, drone, save_action):
        self._drone = drone
        self._save_action = save_action

        self.load_drone()

        super(DroneEditorWindow, self).__init__(parent, self._title, self.save_drone)
        
    def load_drone(self):
        self._drone_name = self._drone.name
        if self._drone_name == '':
            self._title = '<new>'
        else:
            self._title = self._drone_name

        self._drone_class = self._drone.class_type
        self._drone_rescue = self._drone.rescue


    def add_editor_widgets(self):
        """ Adds the widgets for editing a drone. """
        name_label = tk.Label(self.frame, text="Name:")
        self.name_txt_box = tk.Text(self.frame, height=1, width=20)
        self.name_txt_box.insert(tk.END, self._drone_name)
        class_label = tk.Label(self.frame, text="Drone Class:")

        self.class_var = tk.StringVar(self.frame)
        if self._drone_class == 1:
            self.class_var.set("One")
        else:
            self.class_var.set("Two")
        class_option = tk.OptionMenu(self.frame, self.class_var, "One", "Two")

        rescue_label = tk.Label(self.frame, text="Rescue Drone:")

        self.rescue_var = tk.StringVar(self.frame)
        if self._drone_rescue == False:
            self.rescue_var.set("No")
        else:
            self.rescue_var.set("Yes")
        rescue_option = tk.OptionMenu(self.frame, self.rescue_var, "No", "Yes")

        location_label = tk.Label(self.frame, text="Location:")
        location_txt_box = tk.Text(self.frame, height=1, width=20)
        if self._drone.location.is_valid():
            position = str(self._drone.location.position())[0:-4] +')'
            location_txt_box.insert(tk.END, position)
        else:
            location_txt_box.insert(tk.END, "n/a")
        location_txt_box.config(state=tk.DISABLED)

        name_label.grid(in_=self.frame, row=1, column=1, sticky=tk.E)
        self.name_txt_box.grid(in_=self.frame, row=1, column=2, sticky=tk.W)
        class_label.grid(in_=self.frame, row=2, column=1, sticky=tk.E) 
        class_option.grid(in_=self.frame, row=2, column=2, sticky=tk.W)
        rescue_label.grid(in_=self.frame, row=3, column=1, sticky=tk.E)
        rescue_option.grid(in_=self.frame, row=3, column=2, sticky=tk.W)
        location_label.grid(in_=self.frame, row=4, column=1, sticky=tk.E)
        location_txt_box.grid(in_=self.frame, row=4, column=2, sticky=tk.W)

        return 5

    def save_drone(self):
        """ Updates the drone details and calls the save action. """
        self._drone.name = self.name_txt_box.get("1.0", "end-1c")
        if self.class_var.get() == "One":
            self._drone.class_type = 1
        else:
            self._drone.class_type = 2
        if self.rescue_var.get() == "Yes":
            self._drone.rescue = 1
        else:
            self._drone.rescue = 0
        self._save_action(self._drone)

class OperatorEditorWindow(EditorWindow):
    """ Editor window for operators. """

    def __init__(self, parent, operator, save_action):
        self._operator = operator
        self._save_action = save_action

        if self._operator.first_name == None:
            self._title = '<new>'
        else:
            self._title = self._operator.first_name + ' ' + self._operator.family_name

        super(OperatorEditorWindow, self).__init__(parent, self._title, self.save_operator)

    def add_editor_widgets(self):
        """ Adds the widgets for editing a operator. """
        first_name_label = tk.Label(self.frame, text="First Name:")
        self.first_name_txt_box = tk.Text(self.frame, height=1, width=20)
        if self._operator.first_name != None:
            self.first_name_txt_box.insert(tk.END, self._operator.first_name)

        family_name_label = tk.Label(self.frame, text="Family Name:")
        self.family_name_txt_box = tk.Text(self.frame, height=1, width=20)
        if self._operator.family_name != None:
            self.family_name_txt_box.insert(tk.END, self._operator.family_name)

        drone_license_label = tk.Label(self.frame, text="Drone License:")
        self.drone_license_var = tk.StringVar(self.frame)
        if self._operator.drone_license == 2:
            self.drone_license_var.set("Two")
        else:
            self.drone_license_var.set("One")
        drone_license_option = tk.OptionMenu(self.frame, self.drone_license_var, "One", "Two")

        rescue_label = tk.Label(self.frame, text="Rescue Endorsement:")
        self.rescue_txt_box = tk.Text(self.frame, height=1, width=20)
        if self._operator.rescue_endorsement == 1:
            self.rescue_txt_box.insert(tk.END, "Yes")
        else:
            self.rescue_txt_box.insert(tk.END, "No")
        self.rescue_txt_box.config(state=tk.DISABLED)
        
        operations_label = tk.Label(self.frame, text="Number of Operations")
        operations_var = tk.StringVar(self.frame)
        operations_var.set(self._operator.operations)
        self.operations_spinbox = tk.Spinbox(self.frame, from_=0, to=999, textvariable=operations_var)
        
        first_name_label.grid(in_=self.frame, row=1, column=1, sticky=tk.E)
        self.first_name_txt_box.grid(in_=self.frame, row=1, column=2, sticky=tk.W)
        family_name_label.grid(in_=self.frame, row=2, column=1, sticky=tk.E)
        self.family_name_txt_box.grid(in_=self.frame, row=2, column=2, sticky=tk.W)
        drone_license_label.grid(in_=self.frame, row=3, column=1, sticky=tk.E)
        drone_license_option.grid(in_=self.frame, row=3, column=2, sticky=tk.W)
        rescue_label.grid(in_=self.frame, row=4, column=1, sticky=tk.E)
        self.rescue_txt_box.grid(in_=self.frame, row=4, column=2, sticky=tk.W)
        operations_label.grid(in_=self.frame, row=5, column=1, sticky=tk.E)
        self.operations_spinbox.grid(in_=self.frame, row=5, column=2, sticky=tk.W)

        return 6

    def save_operator(self):
        """ Updates the operator details and calls the save action. """
        self._operator.first_name = self.first_name_txt_box.get("1.0", "end-1c")
        self._operator.family_name = self.family_name_txt_box.get("1.0", "end-1c")
        if self.drone_license_var.get() == "One":
            self._operator.drone_license = 1
        else:
            self._operator.drone_license = 2
        self._operator.operations = int(self.operations_spinbox.get())
        if int(self.operations_spinbox.get()) > 4:
            self._operator.rescue_endorsement = 1
        else:
            self._operator.rescue_endorsement = 0

        self._save_action(self._operator)

if __name__ == '__main__':
    conn = mysql.connector.connect(user='root',
                                   password='password',
                                   host='127.0.0.1',
                                   database='dalsys',
                                   charset='utf8')
    app = Application(conn)
    app.main_loop()
    conn.close()
