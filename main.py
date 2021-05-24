import tkinter as tk
from tkinter import ttk

from PyJEM import TEM3
# from PyJEM.offline import TEM3


class App(ttk.Frame):
    def __init__(self, master):
        '''CL3とスポットサイズの制御を行うための処理及びGUIウィンドウの定義'''

        super().__init__(master)
        self.com = TEMCommunicator()
        self.init_vars()
        self.create_widgets()

    def init_vars(self):
        '''ウィジェット変数の定義と初期化'''

        # CL3電流値
        #  TEMCONのLens/Def Monitorの表示と合わせるために16進数文字列表記
        self.var_cl3 = tk.StringVar(value=self.com.GetCL3(hex_str=True))
        # CL3電流値を矢印ボタンで変更するときのステップサイズ(10進)
        self.var_cl3_step = tk.IntVar(value=8)
        # スポットサイズ値
        self.var_spot = tk.IntVar(value=self.com.GetSpotSize())

    def create_widgets(self):
        '''GUIウィンドウの定義'''

        row = 0

        # 現在の電顕側の値を取得するボタンを配置したフレーム
        #  (電顕側で値を変えたときにそれを自動でこちらへ反映する機能をマルチスレッドで実装すればいいが、今回は手動で。)
        frame = ttk.Frame(self)
        ttk.Button(frame, text='Get current values', command=self.get_current_values).grid(row=row, column=0, sticky='W')
        row += 1
        frame.pack(side='top', fill='x', padx=10, pady=10)

        # CL3の制御を行うウィジェットを配置したフレーム
        frame = ttk.Labelframe(self, text='CL3 Lens')
        ttk.Label(frame, text='Value(hex):', width=15).grid(row=row, column=0, sticky='W')
        ttk.Label(frame, width=5, textvariable=self.var_cl3).grid(row=row, column=1, sticky='W')
        ttk.Button(frame, text='◄', command=self.decrement_cl3).grid(row=row, column=2, sticky='E')
        ttk.Button(frame, text='►', command=self.increment_cl3).grid(row=row, column=3, sticky='E')
        row += 1
        ttk.Label(frame, text='Step(decimal):', width=15).grid(row=row, column=0, sticky='W')
        ttk.Entry(frame, textvariable=self.var_cl3_step, width=5).grid(row=row, column=1, sticky='W')
        row += 1
        frame.pack(side='top', fill='x', padx=10, pady=10)

        # スポットサイズの制御を行うウィジェットを配置したフレーム
        frame = ttk.LabelFrame(self, text='Spot Size')
        ttk.Label(frame, text='Value:', width=15).grid(row=row, column=0, sticky='W')
        ttk.Label(frame, width=5, textvariable=self.var_spot).grid(row=row, column=1, sticky='W')
        ttk.Button(frame, text='◄', command=self.decrement_spot).grid(row=row, column=2, sticky='E')
        ttk.Button(frame, text='►', command=self.increment_spot).grid(row=row, column=3, sticky='E')
        row += 1
        frame.pack(side='top', fill='x', padx=10, pady=10)

    def increment_cl3(self):
        step = self.var_cl3_step.get()
        self._change_cl3(step)

    def decrement_cl3(self):
        step = self.var_cl3_step.get()
        self._change_cl3(-1 * step)

    def _change_cl3(self, delta):
        val = hex_string_to_int(self.var_cl3.get())
        val += delta
        if val < 0:
            val = 0
        elif val > 0xFFFF:
            val = 0xFFFF
        self.var_cl3.set(int_to_hex_string(val))
        self.com.SetCL3(val)

    def increment_spot(self):
        self._change_spot(1)

    def decrement_spot(self):
        self._change_spot(-1)

    def _change_spot(self, delta):
        val = self.var_spot.get()
        val += delta
        if val < 1:
            val = 1
        elif val > 5:
            val = 5
        self.var_spot.set(val)
        self.com.SelectSpotSize(val)

    def get_current_values(self):
        '''現在の電顕の設定値を取得する'''

        self.var_cl3.set(self.com.GetCL3(hex_str=True))
        self.var_spot.set(self.com.GetSpotSize())


class TEMCommunicator:
    def __init__(self):
        '''このアプリに必要な電顕インターフェイスをまとめ、ちょっとした処理も行うクラス'''
        # レンズのインターフェイスとなるクラスインスタンス
        self.lens3 = TEM3.Lens3()
        # レンズやデフレクタを除く電子光学系のインターフェイスとなるクラスインスタンス
        self.eos3 = TEM3.EOS3()

    def GetCL3(self, hex_str=False):
        val = self.lens3.GetCL3()
        if hex_str:
            val = int_to_hex_string(val)
        return val

    def SetCL3(self, val):
        if isinstance(val, str):
            val = hex_string_to_int(val)
        self.lens3.SetCL3(val)

    def GetSpotSize(self):
        # PyJEMのスポットサイズ値はTEMCONの表示値よりも1小さいので、TEMCONの表示と併せるために1を加える
        val = self.eos3.GetSpotSize() + 1
        return val

    def SelectSpotSize(self, val):
        # 1を引く理由はGetSpotSizeのコメントを参照
        val -= 1
        self.eos3.SelectSpotSize(val)


def int_to_hex_string(val):
    '''整数値を4桁の大文字16進数表記の文字列に変える'''
    return '{:04x}'.format(val).upper()


def hex_string_to_int(val):
    '''4桁の大文字16進数表記の文字列を整数値に変える'''
    return int(val, 16)


def run_app():
    '''アプリを構成して立ち上げる'''

    root = tk.Tk()
    app = App(master=root)
    app.pack()
    app.master.title('PyJEM Sample App')
    app.mainloop()


if __name__ == '__main__':
    run_app()
