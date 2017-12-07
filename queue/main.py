from queue import QueueSimulater

def mean_list(l):
    return sum(l)/ len(l)

def main(arrival_distro_lambda, service_distro_lambda, n_server, interval, n_customer):
    simulator = QueueSimulater(arrival_distro_lambda=arrival_distro_lambda, service_distro_lambda=service_distro_lambda, n_server=n_server, interval=interval)
    ave_l_queue_list = []
    ave_lining_time_list = []
    rate_lining_list = []

    # シミュレーションを500回行い、平均を取る。
    for i in range(500):
        simulator.initialize(n_customer)
        simulator.simulate(view=False)
        if i == 499:
            average_len_queue, average_lining_time, rate_lining = simulator.describe(plot=False, print_result=False)
            # average_len_queue, average_lining_time, rate_lining = simulator.describe(plot=True, print_result=False) # 待ち時間等をグラフで可視化する場合
            # average_len_queue, average_lining_time, rate_lining = simulator.describe(plot=False, print_result=True) # 行列の動きを可視化する場合
        else:
            average_len_queue, average_lining_time, rate_lining = simulator.describe(plot=False, print_result=False)
        ave_l_queue_list.append(average_len_queue)
        ave_lining_time_list.append(average_lining_time)
        rate_lining_list.append(rate_lining)

    print("到着時間:{0:.3f}分, サービス時間:{1:.3f}分, サーバー数:{2}, 客数:{3}人".format(arrival_distro_lambda, service_distro_lambda, n_server, n_customer))
    print("系内平均人数の平均:{0:.3f}人".format(mean_list(ave_l_queue_list)))
    print("平均待ち時間の平均:{0:.3f}分".format(mean_list(ave_lining_time_list)))
    print("待つ確率の平均:{0:.3f}".format(mean_list(rate_lining_list)))

if __name__ == "__main__":
    main(0.2, 0.5, 2, 0.01, 250)
    main(0.2, 0.5, 3, 0.01, 250)
    main(0.4, 0.5, 2, 0.01, 125)
    main(0.2, 0.4, 2, 0.01, 250)
