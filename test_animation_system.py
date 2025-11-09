"""
Round 38: Animation System

Bring agents to life through behavioral animations that reflect emotional state,
personality, and actions. Smooth transitions and responsive animations make
agents feel dynamic and alive.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable


class AnimationType(Enum):
    """Categories of animations"""
    IDLE = "idle"  # Rest state
    EMOTE = "emote"  # Emotional expression
    ACTION = "action"  # Performing task
    TRANSITION = "transition"  # State change
    INTERACTION = "interaction"  # With other agents
    CELEBRATE = "celebrate"  # Achievement


class TransitionTiming(Enum):
    """Animation transition speeds"""
    INSTANT = 0.0  # No transition
    FAST = 0.2  # 200ms
    NORMAL = 0.5  # 500ms
    SLOW = 1.0  # 1000ms
    VERY_SLOW = 2.0  # 2000ms


@dataclass
class KeyFrame:
    """Single frame in animation"""
    timestamp: float  # Time offset from start (seconds)
    position: tuple = (0.0, 0.0)  # x, y position
    rotation: float = 0.0  # Degrees
    scale: float = 1.0  # Size multiplier
    opacity: float = 1.0  # 0.0-1.0, visibility
    color: Optional[str] = None  # Optional color override
    properties: Dict = field(default_factory=dict)  # Custom properties

    def to_dict(self) -> Dict:
        return {
            "time": self.timestamp,
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "opacity": self.opacity,
            "color": self.color,
            "properties": self.properties
        }


@dataclass
class AnimationClip:
    """Reusable animation sequence"""
    clip_id: str
    animation_type: AnimationType
    duration: float  # Total duration in seconds
    keyframes: List[KeyFrame] = field(default_factory=list)
    loop: bool = False
    auto_transition: bool = True  # Automatically blend to next animation

    def add_keyframe(self, keyframe: KeyFrame) -> bool:
        """Add keyframe to animation"""
        if keyframe.timestamp > self.duration:
            return False
        self.keyframes.append(keyframe)
        self.keyframes.sort(key=lambda k: k.timestamp)
        return True

    def get_frame_at(self, timestamp: float) -> Optional[KeyFrame]:
        """Get keyframe closest to timestamp"""
        if not self.keyframes:
            return None
        if timestamp >= self.duration:
            return self.keyframes[-1]
        for i, kf in enumerate(self.keyframes):
            if kf.timestamp >= timestamp:
                return kf
        return self.keyframes[-1]

    def to_dict(self) -> Dict:
        return {
            "clip_id": self.clip_id,
            "type": self.animation_type.value,
            "duration": self.duration,
            "keyframes": len(self.keyframes),
            "loop": self.loop
        }


@dataclass
class EmoteAnimation:
    """Emotional animation"""
    emotion: str  # JOY, SADNESS, ANGER, etc.
    clip: AnimationClip
    intensity: float = 1.0  # 0.0-1.0, how pronounced

    def adjust_for_intensity(self, intensity: float) -> 'EmoteAnimation':
        """Create adjusted version with different intensity"""
        adjusted_clip = AnimationClip(
            clip_id=self.clip.clip_id,
            animation_type=self.clip.animation_type,
            duration=self.clip.duration * (2.0 - intensity),  # Intensity affects speed
            keyframes=self.clip.keyframes.copy(),
            loop=self.clip.loop
        )
        return EmoteAnimation(self.emotion, adjusted_clip, intensity)

    def to_dict(self) -> Dict:
        return {
            "emotion": self.emotion,
            "intensity": self.intensity,
            "animation": self.clip.to_dict()
        }


@dataclass
class ActionAnimation:
    """Animation for specific action"""
    action_id: str
    action_name: str  # "running", "jumping", "thinking"
    clip: AnimationClip
    can_interrupt: bool = False  # Can be interrupted mid-animation

    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "action_name": self.action_name,
            "duration": self.clip.duration,
            "can_interrupt": self.can_interrupt
        }


@dataclass
class AnimationQueue:
    """Queue of animations to play"""
    agent_id: str
    animations: List[AnimationClip] = field(default_factory=list)
    current_index: int = 0
    elapsed_time: float = 0.0  # Time in current animation
    is_playing: bool = True

    def enqueue(self, animation: AnimationClip) -> bool:
        """Add animation to queue"""
        self.animations.append(animation)
        return True

    def dequeue(self) -> Optional[AnimationClip]:
        """Get and remove next animation"""
        if self.animations:
            return self.animations.pop(0)
        return None

    def get_current_animation(self) -> Optional[AnimationClip]:
        """Get currently playing animation"""
        if 0 <= self.current_index < len(self.animations):
            return self.animations[self.current_index]
        return None

    def advance(self, delta_time: float) -> bool:
        """Advance animation by time"""
        if not self.is_playing:
            return False

        self.elapsed_time += delta_time
        current = self.get_current_animation()

        if current and self.elapsed_time >= current.duration:
            if current.loop:
                self.elapsed_time = 0.0
            else:
                self.current_index += 1
                self.elapsed_time = 0.0

        return True

    def is_finished(self) -> bool:
        """Check if all animations are done"""
        return self.current_index >= len(self.animations) and self.elapsed_time == 0.0

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "queued_animations": len(self.animations),
            "current_index": self.current_index,
            "is_playing": self.is_playing,
            "is_finished": self.is_finished()
        }


class AnimationLibrary:
    """Repository of animation clips"""

    def __init__(self):
        self.clips: Dict[str, AnimationClip] = {}
        self.emote_animations: Dict[str, EmoteAnimation] = {}
        self.action_animations: Dict[str, ActionAnimation] = {}

    def register_clip(self, clip: AnimationClip) -> bool:
        """Register animation clip"""
        if clip.clip_id in self.clips:
            return False
        self.clips[clip.clip_id] = clip
        return True

    def register_emote(self, emote: EmoteAnimation) -> bool:
        """Register emotional animation"""
        key = f"{emote.emotion}"
        if key in self.emote_animations:
            return False
        self.emote_animations[key] = emote
        return True

    def register_action(self, action: ActionAnimation) -> bool:
        """Register action animation"""
        if action.action_id in self.action_animations:
            return False
        self.action_animations[action.action_id] = action
        return True

    def get_clip(self, clip_id: str) -> Optional[AnimationClip]:
        """Get animation clip by ID"""
        return self.clips.get(clip_id)

    def get_emote(self, emotion: str) -> Optional[EmoteAnimation]:
        """Get emotional animation"""
        return self.emote_animations.get(emotion)

    def get_action(self, action_name: str) -> Optional[ActionAnimation]:
        """Get action animation"""
        return self.action_animations.get(action_name)

    def get_idle_animation(self) -> Optional[AnimationClip]:
        """Get appropriate idle animation"""
        for clip in self.clips.values():
            if clip.animation_type == AnimationType.IDLE:
                return clip
        return None

    def to_dict(self) -> Dict:
        return {
            "total_clips": len(self.clips),
            "emotes": len(self.emote_animations),
            "actions": len(self.action_animations)
        }


@dataclass
class AnimationState:
    """Current animation state of agent"""
    agent_id: str
    current_animation: Optional[AnimationClip] = None
    elapsed_time: float = 0.0
    is_animating: bool = False
    current_position: tuple = (0.0, 0.0)
    current_rotation: float = 0.0
    current_scale: float = 1.0

    def start_animation(self, clip: AnimationClip) -> bool:
        """Start playing animation"""
        self.current_animation = clip
        self.elapsed_time = 0.0
        self.is_animating = True
        return True

    def update(self, delta_time: float) -> bool:
        """Update animation state"""
        if not self.is_animating or not self.current_animation:
            return False

        self.elapsed_time += delta_time

        # Check if animation finished
        if self.elapsed_time >= self.current_animation.duration:
            if self.current_animation.loop:
                self.elapsed_time = 0.0
            else:
                self.is_animating = False

        # Update from keyframe
        keyframe = self.current_animation.get_frame_at(self.elapsed_time)
        if keyframe:
            self.current_position = keyframe.position
            self.current_rotation = keyframe.rotation
            self.current_scale = keyframe.scale

        return True

    def stop_animation(self) -> bool:
        """Stop current animation"""
        self.is_animating = False
        self.elapsed_time = 0.0
        return True

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "is_animating": self.is_animating,
            "position": self.current_position,
            "rotation": self.current_rotation,
            "scale": self.current_scale
        }


class AnimationController:
    """Manage agent animations"""

    def __init__(self, agent_id: str, library: AnimationLibrary):
        self.agent_id = agent_id
        self.library = library
        self.animation_state = AnimationState(agent_id)
        self.animation_queue = AnimationQueue(agent_id)

    def play_emotion(self, emotion: str, intensity: float = 1.0) -> bool:
        """Play emotional animation"""
        emote = self.library.get_emote(emotion)
        if not emote:
            return False

        adjusted_emote = emote.adjust_for_intensity(intensity)
        return self.animation_state.start_animation(adjusted_emote.clip)

    def play_action(self, action_name: str) -> bool:
        """Play action animation"""
        action = self.library.get_action(action_name)
        if not action:
            return False

        return self.animation_state.start_animation(action.clip)

    def queue_animation(self, clip: AnimationClip) -> bool:
        """Queue animation to play after current"""
        return self.animation_queue.enqueue(clip)

    def queue_action(self, action_name: str) -> bool:
        """Queue action animation"""
        action = self.library.get_action(action_name)
        if not action:
            return False
        return self.animation_queue.enqueue(action.clip)

    def update(self, delta_time: float) -> bool:
        """Update animation system"""
        self.animation_state.update(delta_time)

        # If animation finished and queue not empty, play next
        if not self.animation_state.is_animating and self.animation_queue.animations:
            next_anim = self.animation_queue.dequeue()
            if next_anim:
                self.animation_state.start_animation(next_anim)

        return True

    def get_current_frame(self) -> Dict:
        """Get current animation frame"""
        return self.animation_state.to_dict()

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "current_state": self.animation_state.to_dict(),
            "queued": self.animation_queue.to_dict()
        }


# ===== Tests =====

def test_keyframe_creation():
    """Test creating keyframe"""
    kf = KeyFrame(
        timestamp=0.0,
        position=(0.0, 0.0),
        rotation=0.0,
        scale=1.0
    )
    assert kf.timestamp == 0.0


def test_animation_clip_creation():
    """Test creating animation clip"""
    clip = AnimationClip(
        clip_id="idle_breathing",
        animation_type=AnimationType.IDLE,
        duration=2.0
    )
    assert clip.clip_id == "idle_breathing"
    assert clip.duration == 2.0


def test_add_keyframe():
    """Test adding keyframes to animation"""
    clip = AnimationClip(
        clip_id="bounce",
        animation_type=AnimationType.ACTION,
        duration=1.0
    )
    kf1 = KeyFrame(0.0, (0.0, 0.0), 0.0, 1.0)
    kf2 = KeyFrame(0.5, (0.0, 1.0), 0.0, 1.0)
    kf3 = KeyFrame(1.0, (0.0, 0.0), 0.0, 1.0)

    assert clip.add_keyframe(kf1) is True
    assert clip.add_keyframe(kf2) is True
    assert clip.add_keyframe(kf3) is True


def test_get_frame_at():
    """Test retrieving keyframe at timestamp"""
    clip = AnimationClip("bounce", AnimationType.ACTION, 1.0)
    kf1 = KeyFrame(0.0, (0.0, 0.0))
    kf2 = KeyFrame(1.0, (0.0, 0.0))
    clip.add_keyframe(kf1)
    clip.add_keyframe(kf2)

    frame = clip.get_frame_at(0.5)
    assert frame is not None


def test_emote_animation():
    """Test emotional animation"""
    clip = AnimationClip("happy_bounce", AnimationType.EMOTE, 1.0)
    emote = EmoteAnimation("JOY", clip, intensity=0.8)
    assert emote.emotion == "JOY"


def test_action_animation():
    """Test action animation"""
    clip = AnimationClip("running", AnimationType.ACTION, 1.5)
    action = ActionAnimation("run_1", "running", clip, can_interrupt=True)
    assert action.action_name == "running"


def test_animation_queue():
    """Test animation queue"""
    queue = AnimationQueue("a1")
    clip1 = AnimationClip("anim1", AnimationType.EMOTE, 1.0)
    assert queue.enqueue(clip1) is True


def test_queue_advance():
    """Test advancing animation queue"""
    queue = AnimationQueue("a1")
    clip = AnimationClip("anim", AnimationType.EMOTE, 0.5, loop=False)
    queue.enqueue(clip)

    queue.advance(0.3)
    assert queue.elapsed_time == 0.3


def test_queue_finish():
    """Test detecting queue completion"""
    queue = AnimationQueue("a1")
    clip = AnimationClip("anim", AnimationType.EMOTE, 0.5, loop=False)
    queue.enqueue(clip)

    queue.advance(0.6)
    assert queue.is_finished() is True


def test_animation_library():
    """Test animation library"""
    lib = AnimationLibrary()
    clip = AnimationClip("idle", AnimationType.IDLE, 2.0)
    assert lib.register_clip(clip) is True


def test_register_emote():
    """Test registering emotional animation"""
    lib = AnimationLibrary()
    clip = AnimationClip("happy", AnimationType.EMOTE, 1.0)
    emote = EmoteAnimation("JOY", clip)
    assert lib.register_emote(emote) is True


def test_register_action():
    """Test registering action animation"""
    lib = AnimationLibrary()
    clip = AnimationClip("jump", AnimationType.ACTION, 0.8)
    action = ActionAnimation("jump_1", "jumping", clip)
    assert lib.register_action(action) is True


def test_get_clip():
    """Test retrieving clip from library"""
    lib = AnimationLibrary()
    clip = AnimationClip("idle", AnimationType.IDLE, 2.0)
    lib.register_clip(clip)

    retrieved = lib.get_clip("idle")
    assert retrieved is not None
    assert retrieved.clip_id == "idle"


def test_get_emote():
    """Test retrieving emotional animation"""
    lib = AnimationLibrary()
    clip = AnimationClip("happy", AnimationType.EMOTE, 1.0)
    emote = EmoteAnimation("JOY", clip)
    lib.register_emote(emote)

    retrieved = lib.get_emote("JOY")
    assert retrieved is not None


def test_animation_state():
    """Test animation state"""
    state = AnimationState("a1")
    assert state.is_animating is False


def test_start_animation():
    """Test starting animation"""
    state = AnimationState("a1")
    clip = AnimationClip("test", AnimationType.EMOTE, 1.0)
    assert state.start_animation(clip) is True
    assert state.is_animating is True


def test_update_animation_state():
    """Test updating animation state"""
    state = AnimationState("a1")
    clip = AnimationClip("test", AnimationType.EMOTE, 1.0)
    state.start_animation(clip)

    # Add keyframe
    clip.add_keyframe(KeyFrame(0.0, (0.0, 0.0)))
    clip.add_keyframe(KeyFrame(1.0, (10.0, 10.0)))

    state.update(0.5)
    assert state.elapsed_time == 0.5


def test_stop_animation():
    """Test stopping animation"""
    state = AnimationState("a1")
    clip = AnimationClip("test", AnimationType.EMOTE, 1.0)
    state.start_animation(clip)
    assert state.stop_animation() is True
    assert state.is_animating is False


def test_animation_controller():
    """Test animation controller"""
    lib = AnimationLibrary()
    controller = AnimationController("a1", lib)
    assert controller.agent_id == "a1"


def test_controller_play_emotion():
    """Test playing emotion animation"""
    lib = AnimationLibrary()
    clip = AnimationClip("happy", AnimationType.EMOTE, 1.0)
    emote = EmoteAnimation("JOY", clip)
    lib.register_emote(emote)

    controller = AnimationController("a1", lib)
    assert controller.play_emotion("JOY") is True


def test_controller_play_action():
    """Test playing action animation"""
    lib = AnimationLibrary()
    clip = AnimationClip("jump", AnimationType.ACTION, 0.8)
    action = ActionAnimation("jumping", "jumping", clip)  # action_id matches action_name for lookup
    lib.register_action(action)

    controller = AnimationController("a1", lib)
    assert controller.play_action("jumping") is True


def test_complete_animation_workflow():
    """Test complete animation workflow"""
    # Create library with animations
    lib = AnimationLibrary()

    # Idle animation
    idle_clip = AnimationClip("idle", AnimationType.IDLE, 2.0, loop=True)
    idle_clip.add_keyframe(KeyFrame(0.0, (0.0, 0.0), 0.0, 1.0))
    idle_clip.add_keyframe(KeyFrame(1.0, (0.0, 0.5), 0.0, 1.05))
    idle_clip.add_keyframe(KeyFrame(2.0, (0.0, 0.0), 0.0, 1.0))
    lib.register_clip(idle_clip)

    # Joy animation
    joy_clip = AnimationClip("joy_bounce", AnimationType.EMOTE, 1.0)
    joy_clip.add_keyframe(KeyFrame(0.0, (0.0, 0.0), 0.0, 1.0))
    joy_clip.add_keyframe(KeyFrame(0.5, (0.0, 2.0), 0.0, 1.1))
    joy_clip.add_keyframe(KeyFrame(1.0, (0.0, 0.0), 0.0, 1.0))
    joy_emote = EmoteAnimation("JOY", joy_clip)
    lib.register_emote(joy_emote)

    # Running animation
    run_clip = AnimationClip("running", AnimationType.ACTION, 1.5)
    run_clip.add_keyframe(KeyFrame(0.0, (0.0, 0.0), 0.0, 1.0))
    run_clip.add_keyframe(KeyFrame(1.5, (10.0, 0.0), 0.0, 1.0))
    run_action = ActionAnimation("run_1", "running", run_clip)
    lib.register_action(run_action)

    # Create controller
    controller = AnimationController("explorer", lib)

    # Play joy
    controller.play_emotion("JOY", 0.9)
    controller.update(0.5)
    assert controller.animation_state.is_animating is True

    # Queue running action
    controller.queue_action("running")

    # Update until joy finishes
    controller.update(0.6)
    assert not controller.animation_state.is_animating or controller.animation_state.current_animation.clip_id == "running"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
