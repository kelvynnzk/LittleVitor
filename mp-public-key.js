// Chave PÚBLICA do Mercado Pago — diferente do Access Token (que é
// secreto e só existe no back-end), essa aqui é feita pra ficar no
// navegador: é assim que o Card Payment Brick consegue tokenizar o
// cartão sem que o número dele passe pelo nosso servidor.
//
// Preencha com a sua "Public Key" de TESTE, encontrada em:
// https://www.mercadopago.com.br/developers/panel -> sua aplicação
// -> "Credenciais de teste".
const MP_PUBLIC_KEY = "TEST-aca258d6-1d8f-4dec-be90-697418e90719";
