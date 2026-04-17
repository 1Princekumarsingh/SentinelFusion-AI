from deep_sort_realtime.deepsort_tracker import DeepSort

class ObjectTracker:
    def __init__(self):
        self.tracker = DeepSort(max_age=20, n_init=3, max_cosine_distance=0.6)

    def update(self, frame, detections):
        tracks = self.tracker.update_tracks(detections, frame=frame)
        tracked_objects = []

        for track in tracks:
            if not track.is_confirmed(): # only use tracks that are seen enough times
                continue
            if track.hits < 3:
                continue
            if track.time_since_update > 2:
                continue

            track_id = track.track_id
            l, t, r, b = map(int, track.to_ltrb())

            tracked_objects.append({
                "id": track_id,
                "bbox": (l, t, r, b)
            })

        return tracked_objects