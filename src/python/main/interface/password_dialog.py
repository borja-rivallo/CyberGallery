from tkinter import simpledialog, messagebox

def ask_encryption_password(parent, account_manager, current_user):
    """Diálogo para solicitar contraseña"""
    password = simpledialog.askstring(
        "Encriptación de obra",
        "Ingresa tu contraseña para encriptar la obra:\n"
        "   - Si la obra es pública, se usará una contraseña por defecto\n"
        "   - Si la obra es privada, se usará la contraseña que ingreses aquí\n",
        show='*',
        parent=parent
    )
    
    if password:
        # Verificar la contraseña introducida
        try:
            if not account_manager.login_user(current_user, password):
                messagebox.showerror("Error", "Contraseña incorrecta")
                return None
        except Exception as e:
            print(f"Error verificando contraseña: {e}")
            if not messagebox.askyesno("Advertencia", "No se pudo verificar la contraseña. ¿Continuar igualmente?"):
                return None
    
    return password
