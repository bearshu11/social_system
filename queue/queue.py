import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

class QueueSimulater():
    def __init__(self, arrival_distro_lambda=3, service_distro_lambda=3, n_server=2, len_queue=float('infinity'), interval=0.01, debug=False):
        """
        待ち行列をコントロールするためのクラス

        Parameter
        ----------
        arrival_distro_lambda: float
        客の到着間隔の平均時間
        service_distro_lambda: float
        サービスの平均時間
        n_server: int
        サーバーの数
        len_queue: int or float('infinity')
        行列の最大長さ
        interval: float
        シミュレーションする際の時間ステップの間隔
        ただし、1*10^(?)を満たす正の小数とする(?は任意の整数)。
        debug: boolean
        デバッグを出力するか否か

        Other Instance Variables
        ----------
        self.queue: Queue
        対象の待ち行列
        self.arrival_time_sequence: list(float)
        到着時刻の数列
        self.service_time_sequence: list(float)
        サービス時間の数列
        self.time: float
        シミュレーションをする際の時間
        self.number: int
        現在、待ち行列に何人到着したかを表す
        self.people_log: list(person)
        待ち行列に並んだPersonのログ
        self.line_length_log: list(int)
        待ち行列の長さのログ
        """

        self.arrival_distro_lambda = arrival_distro_lambda
        self.service_distro_lambda = service_distro_lambda
        self.n_server = n_server
        self.len_queue = len_queue
        self.interval = interval
        self.debug = debug

    def initialize(self, len_simulation):
        """
        __init__で設定された値を元に、指数分布に従って、
        到着間隔・サービス時間の数列を作り、待ち行列のシミュレーション環境を整える。

        Parameter
        ----------
        len_simulation: int
        客の来店者数
        """

        self.queue = Queue(self.n_server, self.interval)

        # 数値の桁数をself.intervalに合わせた到着間隔・サービス時間の数列を作成
        tmp = self.interval
        decimal = 0
        while True:
            if tmp >= 1:
                break
            else:
                decimal += 1
                tmp *= 10
        self.arrival_time_sequence = list(np.round(np.cumsum(self.exponential_distribution(self.arrival_distro_lambda, len_simulation)), decimal))
        self.service_time_sequence = list(np.round(self.exponential_distribution(self.service_distro_lambda, len_simulation), decimal))

        self.time = 0
        self.number = 0
        self.people_log = []
        self.line_length_log = []

        if self.debug:
            print("到着時刻:",self.arrival_time_sequence)
            print("サービス時間:", self.service_time_sequence)

    def exponential_distribution(self, lam, length):
        """
        指数分布に従う乱数列を、逆関数法を用いて算出する。

        Parameter
        ----------
        lam: float
        指数分布の期待値
        length: int
        乱数列の長さ

        Return
        ---------
        exponential_distribution_sequence: list(float)
        指数分布に従った乱数列
        """

        random_sequence = np.random.rand(length)
        exponential_distribution_sequence = - (lam) * np.log(random_sequence)

        return exponential_distribution_sequence

    def step(self, view=True):
        """
        シミュレーションの時間を１単位進め、待ち行列の状況を変化させる。

        Parameter
        ---------
        view: boolean
        現在の待ち行列の形状を出力するか否か。
        """

        self.time += self.interval

        # 待ち行列に到着するPersonを作成する。
        people = []
        while self.number < len(self.arrival_time_sequence)-1:
            next_arrival_time = self.arrival_time_sequence[self.number]
            if next_arrival_time <= self.time:
                next_service_time = self.service_time_sequence[self.number]
                person = Person(next_arrival_time, next_service_time)
                people.append(person)
                self.number += 1
            else:
                break

        visited_people, line_length = self.queue.step(people)

        self.people_log.extend(visited_people)
        self.line_length_log.append(line_length)

        if view:
            self.view()

    def simulate(self, view=True):
        """
        シミュレーションを最後まで実行する

        Parameter
        --------
        view: boolean
        現在の待ち行列の形状を出力するか否か。
        """

        while (self.number < len(self.arrival_time_sequence)-1) or (len(self.queue.lining_people)>0):
            self.step(view=view)

    def view(self):
        """
        待ち行列の形状を * を人に見立てて出力する
        """

        star = "*"
        queue_length = len(self.queue.lining_people)
        if self.n_server > queue_length:
            print(star * queue_length)
        else:
            served_people = star * self.n_server
            lining_people = star * (queue_length - self.n_server)
            print(served_people + "   " + lining_people)

    def describe(self, plot=True, print_result=False):
        """
        シミュレーション結果を出力する。

        Parameter
        ----------
        plot: boolean
        待ち時間・系内人数の分布のグラフを出力するか否か。
        print_result: boolean
        結果を表示するか否か。

        Return
        ----------
        average_len_queue: float
        列の長さの平均
        average_lining_time: float
        平均待ち時間
        rate_lining: float
        待つ確率
        """

        lining_time_list = []
        id_list = []
        zero_count = 0
        for person in self.people_log:
            lining_time_list.append(person.lining_time)
            id_list.append(person.id)
            if person.lining_time == 0:
                zero_count += 1

        if self.debug:
            print("id", id_list)

        if plot:
            plt.figure()
            plt.hist(lining_time_list)
            plt.title("待ち時間分布")
            plt.savefig("lining_time.png")
            plt.figure()
            plt.hist(self.line_length_log)
            plt.title("待ち人数分布")
            plt.savefig("line_length.png")

        average_len_queue = sum(self.line_length_log)/len(self.line_length_log)
        average_lining_time = sum(lining_time_list)/len(lining_time_list)
        rate_lining = 1-zero_count/len(lining_time_list)

        if print_result:
            print("系内平均人数：{}人".format(average_len_queue))
            print("平均待ち時間：{}分".format(average_lining_time))
            print("待つ確率：{}".format(rate_lining))

        return average_len_queue, average_lining_time, rate_lining

class Queue():
    def __init__(self, n_server, interval):
        """
        待ち行列そのものを表現するクラス

        Parameter
        ----------
        n_server: int
        サーバーの数
        interval: float
        シミュレーションする際の時間ステップの間隔
        ただし、1*10^(?)を満たす正の小数とする(?は任意の整数)。
        """

        self.n_server = n_server
        self.lining_people = []
        self.time = 0
        self.interval = interval

    def get_lining_time(self):
        """
        現在の待ち行列に並ぶときの列に並ぶ時間を算出する。
        """

        if self.n_server > len(self.lining_people):
            return 0.0
        max_left_time_list = sorted(self.get_left_time_list(self.lining_people))
        return max_left_time_list[len(self.lining_people) - self.n_server]

    def get_left_time_list(self, people):
        """
        人々の列を脱出するまでの残り時間を算出する

        Paremeter
        ----------
        people: list(Person)
        残り時間を算出したいPersonのlist
        """

        def get_left_time(person):
            elapsed_time = self.time - person.arrival_time
            return person.wating_time - elapsed_time

        left_time_list = map(get_left_time, people)
        return left_time_list

    def get_left_time(self, person):
        """
        列を脱出するまでの残り時間を算出する。

        Parameter
        ---------
        person: Person
        残り時間を計算するPerson
        """

        elapsed_time = self.time - person.arrival_time
        return person.wating_time - elapsed_time

    def step(self, come_people):
        """
        時間を１単位進めて、行列の状況を変化させる

        Paremeter
        ---------
        come_people: list(person)
        待ち行列に到着したPersonのlist

        Return
        ---------
        visited_people: list(person)
        待ち行列から脱出したPersonのlist
        len(self.lining_people): int
        現在の待ち行列に並んでいる人数
        """

        self.time += self.interval

        # 待ち行列から出ていくPersonの処理
        visited_people = []
        while True:
            break_flag = True
            remove_indices = []
            l = self.n_server
            if self.n_server > len(self.lining_people):
                l =  len(self.lining_people)
            for index, served_person in enumerate(self.lining_people[0:l]):
                left_time = self.get_left_time(served_person)
                if left_time <= 0:
                    break_flag = False
                    visited_people.append(served_person)
                    remove_indices.append(index)

            if break_flag:
                break

            dellist = lambda items, indexes: [item for index, item in enumerate(items) if index not in indexes]
            self.lining_people = dellist(self.lining_people, remove_indices)

        # 待ち行列に到着したPersonの処理
        for person in come_people:
            lining_time = self.get_lining_time()
            person.set_lining_wating_time(lining_time)
            self.lining_people.append(person)

        return visited_people, len(self.lining_people)

class Person():
    # 現在のmaxのidを格納するクラス変数
    person_id = 0

    def __init__(self, arrival_time, service_time):
        """
        待ち行列に並ぶ人を表現するクラス

        Parameter
        ----------
        arrival_time: float
        待ち行列に到着する時刻
        service_time: float
        サービスを受ける時間

        Other Instance Variables
        ----------
        self.id: int(>0)
        IDを表す
        self.lining_time: float
        列に並んで待つ時間
        self.wating_time: float
        総所要時間
        """

        self.arrival_time = arrival_time
        self.service_time = service_time
        self.id = self.__class__.person_id
        self.__class__.person_id += 1

    def set_lining_wating_time(self, lining_time):
        """
        列に並んで待つ時間・全ての所要時間を設定する。

        Parameter
        ---------
        lining_time: float
        列に並んで待つ時間
        """

        self.lining_time = lining_time
        self.wating_time = self.service_time + self.lining_time
