import control as ctrl
import cv2
import serial
import numpy as np
import time

# Defina a porta serial que o Arduino está conectado (substitua 'COM3' pela porta do seu Arduino)
porta_serial = serial.Serial("COM4",9600)
# Aguarda um tempo para garantir que a conexão foi estabelecida
time.sleep(2)

# VALORES DE REFERÊNCIA DO SISTEMA
reference_x = 0
reference_y = 0


# FUNÇÃO DE TRANSFERÊNCIA DO CONTROLADOR (para T = 2/30)
num_controller_discrete = [0.3806, 0.1692, -0.2114]
den_controller_discrete = [1, -1.012, 0.2573]

GCO_discrete = ctrl.TransferFunction(num_controller_discrete, den_controller_discrete, dt=2/30)  # dt=2/30 indica amostragem em segundos, baseado no tempo de amostragem da câmera

print("Função de Transferência:")
print(GCO_discrete)


# FUNÇÃO DE DETECÇÃO DA POSIÇÃO DA BOLA E CONTROLE
def detect_ball_and_control():
    cap = cv2.VideoCapture(0)  # No parentesis o número depende de quantas câmeras estão instaladas no PC. Se for uma única é 0
    #PC Su
    roi_x = 120               #TODOS OS VALORES ABAIXO PRECISAM SER REGULADOS DE ACORDO COM A POSIÇÃO DA CÂMERA
    roi_y = 20
    roi_width = 430
    roi_height = 430

    # Tamanho do prato em pixels (largura e altura)
    plate_width_px = roi_width
    plate_height_px = roi_height

    # Tamanho do prato em centímetros
    plate_width_cm = 30  # DEFINIR O VALOR DE ACORDO COM O TAMANHO DO PRATO UTILIZADO
    plate_height_cm = 30

    # Posição anterior da bola
    prev_position = None

    # Ajuste dos parâmetros da câmera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Largura da imagem
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Altura da imagem
    cap.set(cv2.CAP_PROP_FPS, 30)  # Taxa de quadros por segundo

    start_time = time.time()

    while True:

        start_time = time.time()
        
        ret, frame = cap.read()

        if not ret:
            break

        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)
        roi = frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=20,
            param1=50,
            param2=30,
            minRadius=10,
            maxRadius=50,
        )

        if circles is not None:
            circles = np.uint16(np.around(circles))
            largest_circle = max(circles[0, :], key=lambda x: x[2])
            center = (largest_circle[0], largest_circle[1])

            # Converte as coordenadas do centro da bola para centímetros
            x_px, y_px = center
            x_cm = ((x_px / plate_width_px) * plate_width_cm) - 15
            y_cm = ((y_px / plate_height_px) * plate_height_cm) - 15


            print(f"Posição da Bola: X={x_cm} cm, Y={y_cm} cm")


            # DEFININDO O ERRO

            # Erros de posição
            error_x = reference_x - x_cm
            error_y = reference_y - y_cm
            #print(f"Erro em: X={error_x} cm, Y={error_y} cm")
            
            # Aplique o controlador para obter o ângulo
            _, angle_Theta_alpha = ctrl.forced_response(GCO_discrete, [0, 1], error_x)

            _, angle_Theta_beta = ctrl.forced_response(GCO_discrete, [0, 1], error_y)

            print("Saída do Controlador em X:", angle_Theta_alpha[1])
            #print(angle_Theta_alpha[1])
            print("Saída do Controlador em Y", angle_Theta_beta[1])
            #print(angle_Theta_beta[1])
            print("")

            # Verificar se ambas as coordenadas são positivas ou ambas são negativas
            if (angle_Theta_alpha[1] > 0 and angle_Theta_beta[1] > 0) or (angle_Theta_alpha[1] < 0 and angle_Theta_beta[1] < 0):
                # Inverter os valores
                angle_Theta_alpha[1] = -angle_Theta_alpha[1]
                angle_Theta_beta[1] = -angle_Theta_beta[1]

            # Convertendo as coordenadas x e y para números inteiros
            x = int(angle_Theta_alpha[1]) + 90
            y = int(angle_Theta_beta[1]) + 90

            data = f"{x},{y}\n"
            print("Valor arduino:", data)
            porta_serial.write(data.encode())  # Convertendo para bytes antes de enviar
            #time.sleep(0.5)

            end_time = time.time()
            elapsed_time = end_time - start_time

            print(f"Tempo da passagem: {elapsed_time:.6f} segundos")

            #Ajuste do tempo de espera com base no tempo de amostragem definido e o tempo de processamento real
            time.sleep(2/30 - elapsed_time)

           
        cv2.imshow("Bola e Plate", frame)


        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    
   # porta_serial.close()        
    cap.release()
    cv2.destroyAllWindows()

    

# Exemplo de uso da função
if __name__ == "__main__":
    print("Pressione 'q' para sair do programa.")
    detect_ball_and_control()
