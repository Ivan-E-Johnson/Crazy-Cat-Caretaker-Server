from Home import *
import threading
import subprocess

doc_ref = db.collection("Home").document("12345")
house: House = House.get("12345")
processes = {}
# Define the callback function that will be triggered when the document changes
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(f'Received document snapshot: {doc.id}')
        events = doc.to_dict()["events"]
        for change in changes:
            if change.type.name == 'ADDED':
                print(f'New House: {change.document.id}')
            elif change.type.name == 'MODIFIED':
                if(events["laser_changed"] == True):
                    print(f'Modified House: {change.document.id} and Turned on the laser with mode {events["laser_state"]}')
                    house.events.laser_changed = False
                    house.events.laser_state = events["laser_state"]
                    house.create()
                    command = ['python', 'example.py', '-t 5', '-m', str(events["laser_state"])]

                    # Run the command asynchronously and capture the output
                    processes["Laser"]= subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # Do other things while the command runs asynchronously
                    print("Running command in the background...")


                elif(events["dispense_changed"] == True):
                    print(f'Modified House: {change.document.id}, Dispensing: {events["dispense_amount"]} units of food')
                else:
                    print(f'Modified House: {change.document.id} somehow?')
            elif change.type.name == 'REMOVED':
                print(f'Removed House: {change.document.id}')

# Watch the document for changes
doc_watch = doc_ref.on_snapshot(on_snapshot)


while True:
    pass
#     # # Wait for the command to finish and get the output
#
