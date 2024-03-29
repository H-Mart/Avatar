from .receiver import Receiver, columns

import numpy as np
import pandas as pd
from pathlib import Path
from time import time


class BrainwaveRecorder:
    def __init__(self, sampling_rate, recording_dir: Path | str):
        self.receiver = Receiver(sampling_rate)
        self.recording_dir = Path(recording_dir)
        self.recording_dir.mkdir(exist_ok=True)
        self.cancelled = False

    def cancel_recording(self):
        self.receiver.stop()
        self.cancelled = True

    def record(self, duration: int, label: str, **additional_columns):
        self.cancelled = False
        start = time()
        data = []
        with self.receiver as recv:
            for sample in recv:
                data.append(sample)
                if time() - start >= duration:
                    break

        data = np.vstack(data)
        df = pd.DataFrame(data, columns=columns)
        df['label'] = label

        for k, v in additional_columns.items():
            df[k] = v

        df.to_csv(self.recording_dir / f'{label}_{int(time())}.csv', index=False)

        print(f'recording time {time() - start}')

        return df
