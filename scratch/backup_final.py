import shutil
shutil.copy2("E:/workspace/agy/AI_TEST/index.html", "E:/workspace/agy/AI_TEST/backups/index.html.sidebar.bak")
shutil.copy2("E:/workspace/agy/AI_TEST/index.html", "E:/workspace/agy/AI_TEST/backups/index.html.bak") # Overwrite general backup too
print("Backed up final index.html to backups/")
