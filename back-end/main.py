from usuarios import cadastro,login


def menu():
 """Loop principal do programa. Fica rodando repetidamente,mostrando as opções, até o usuário escolher sair."""

 log_user= None
 while True:
    
    print("\n--- Sistema de Login ---")
    print("1. Cadastrar")
    print("2. Login")
    print("3. Sair")

    opcao =input("Escolha uma opção :")

    if opcao == "1":
     nome = input("Nome : ")
     email = input("email: ")
     senha = input("senha : ")
     cadastro(nome ,email ,senha)

    
    elif opcao == "2":
     email=input("Email : ")
     senha=input("senha : ")
     log_user =login(email,senha)

    elif opcao=="3":
     if log_user:
      print(f"Saindo do sistema, até a próxima {log_user['nome']}...")
     else:
      print("Saindo do sitema...")
     break
    else:
     print("opção inválida") 

if __name__ == "__main__":
 menu()