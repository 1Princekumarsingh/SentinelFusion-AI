from deep_sort_realtime.deepsort_tracker import DeepSort

class ObjectTracker:
    def __init__(
        self,
        max_age=30,
        n_init=3,
        max_cosine_distance=0.3,
        min_hits=3,
        max_time_since_update=2,
    ):
        self.tracker = DeepSort(
            max_age=max_age,
            n_init=n_init,
            max_cosine_distance=max_cosine_distance,
        )
        self.min_hits = int(min_hits)
        self.max_time_since_update = int(max_time_since_update)

    def update(self, frame, detections):
        tracks = self.tracker.update_tracks(detections, frame=frame)
        tracked_objects = []

        for track in tracks:
            if not track.is_confirmed(): # only use tracks that are seen enough times
                continue
            if track.hits < self.min_hits:
                continue
            if track.time_since_update > self.max_time_since_update:
                continue

            track_id = track.track_id
            l, t, r, b = map(int, track.to_ltrb())

            tracked_objects.append({
                "id": track_id,
                "bbox": (l, t, r, b)
            })

        return tracked_objects
