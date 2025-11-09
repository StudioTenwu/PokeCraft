"""
Round 52: Multi-Modal Perception System
Enable agents to perceive and process multiple types of input (text, vision, audio).
Features: sensory input processing, feature extraction, attention mechanisms, sensory fusion.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class ModalityType(Enum):
    """Type of sensory input"""
    TEXT = "text"
    VISION = "vision"
    AUDIO = "audio"
    TACTILE = "tactile"
    PROPRIOCEPTION = "proprioception"


class AttentionLevel(Enum):
    """How much attention agent pays to stimulus"""
    IGNORE = 0.0
    MINIMAL = 0.2
    LOW = 0.4
    MODERATE = 0.6
    HIGH = 0.8
    INTENSE = 1.0


@dataclass
class SensoryInput:
    """Input from one sensory modality"""
    input_id: str
    modality: ModalityType
    content: str
    intensity: float  # 0.0-1.0, strength of stimulus
    timestamp: float = 0.0
    emotional_valence: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    attention_required: float = 0.5  # 0.0-1.0

    def to_dict(self) -> Dict:
        return {
            "id": self.input_id,
            "modality": self.modality.value,
            "intensity": self.intensity,
            "attention": self.attention_required,
            "valence": self.emotional_valence
        }


@dataclass
class PerceptualFeature:
    """Extracted feature from sensory input"""
    feature_id: str
    feature_type: str  # "edges", "colors", "phonemes", "sentiment", etc.
    source_input: str  # input_id it came from
    value: Any
    confidence: float = 0.7  # 0.0-1.0
    salience: float = 0.5  # 0.0-1.0, how important/noticeable

    def to_dict(self) -> Dict:
        return {
            "id": self.feature_id,
            "type": self.feature_type,
            "confidence": self.confidence,
            "salience": self.salience
        }


@dataclass
class Percept:
    """Unified perception combining multiple modalities"""
    percept_id: str
    inputs: List[SensoryInput] = field(default_factory=list)
    features: List[PerceptualFeature] = field(default_factory=list)
    integrated_meaning: str = ""
    understanding_confidence: float = 0.0
    emotional_response: float = 0.0  # -1.0 to 1.0

    def add_input(self, sensory_input: SensoryInput) -> bool:
        """Add sensory input to percept"""
        self.inputs.append(sensory_input)
        return True

    def add_feature(self, feature: PerceptualFeature) -> bool:
        """Add extracted feature"""
        self.features.append(feature)
        return True

    def get_modalities(self) -> List[ModalityType]:
        """Get all modalities in this percept"""
        return list(set(inp.modality for inp in self.inputs))

    def is_multimodal(self) -> bool:
        """Check if percept uses multiple modalities"""
        return len(self.get_modalities()) > 1

    def to_dict(self) -> Dict:
        return {
            "id": self.percept_id,
            "modalities": len(self.get_modalities()),
            "features": len(self.features),
            "confidence": self.understanding_confidence
        }


class ModalityProcessor:
    """Process input from specific modality"""

    def __init__(self, modality: ModalityType):
        self.modality = modality
        self.processed_count = 0

    def process(self, sensory_input: SensoryInput) -> List[PerceptualFeature]:
        """Process input and extract features"""
        self.processed_count += 1
        features = []

        if self.modality == ModalityType.TEXT:
            features = self._process_text(sensory_input)
        elif self.modality == ModalityType.VISION:
            features = self._process_vision(sensory_input)
        elif self.modality == ModalityType.AUDIO:
            features = self._process_audio(sensory_input)
        elif self.modality == ModalityType.TACTILE:
            features = self._process_tactile(sensory_input)

        return features

    def _process_text(self, input: SensoryInput) -> List[PerceptualFeature]:
        """Extract features from text"""
        features = []

        # Word count feature
        words = len(input.content.split())
        features.append(PerceptualFeature(
            f"feat_{self.processed_count}_wc",
            "word_count",
            input.input_id,
            words,
            confidence=0.95,
            salience=0.3
        ))

        # Sentiment feature (simplified)
        sentiment = 0.5  # Neutral default
        if any(word in input.content.lower() for word in ["great", "good", "excellent"]):
            sentiment = 0.8
        elif any(word in input.content.lower() for word in ["bad", "terrible", "awful"]):
            sentiment = 0.2

        features.append(PerceptualFeature(
            f"feat_{self.processed_count}_sent",
            "sentiment",
            input.input_id,
            sentiment,
            confidence=0.7,
            salience=0.6
        ))

        return features

    def _process_vision(self, input: SensoryInput) -> List[PerceptualFeature]:
        """Extract features from vision"""
        features = []

        # Brightness feature
        features.append(PerceptualFeature(
            f"feat_{self.processed_count}_bright",
            "brightness",
            input.input_id,
            input.intensity,
            confidence=0.9,
            salience=0.5
        ))

        # Size/scale feature
        features.append(PerceptualFeature(
            f"feat_{self.processed_count}_scale",
            "scale",
            input.input_id,
            len(input.content),
            confidence=0.8,
            salience=0.4
        ))

        return features

    def _process_audio(self, input: SensoryInput) -> List[PerceptualFeature]:
        """Extract features from audio"""
        features = []

        # Loudness feature
        features.append(PerceptualFeature(
            f"feat_{self.processed_count}_loud",
            "loudness",
            input.input_id,
            input.intensity,
            confidence=0.85,
            salience=0.7
        ))

        return features

    def _process_tactile(self, input: SensoryInput) -> List[PerceptualFeature]:
        """Extract features from tactile sensation"""
        features = []

        # Pressure feature
        features.append(PerceptualFeature(
            f"feat_{self.processed_count}_press",
            "pressure",
            input.input_id,
            input.intensity,
            confidence=0.8,
            salience=0.6
        ))

        return features

    def to_dict(self) -> Dict:
        return {
            "modality": self.modality.value,
            "processed": self.processed_count
        }


class AttentionMechanism:
    """Controls what agent pays attention to"""

    def __init__(self):
        self.attention_weights: Dict[str, float] = {}
        self.focus: Optional[str] = None  # Currently focused input_id
        self.attention_history: List[Tuple[str, float]] = []

    def set_attention(self, input_id: str, level: float) -> bool:
        """Set attention level to input (0.0-1.0)"""
        if not (0.0 <= level <= 1.0):
            return False

        self.attention_weights[input_id] = level

        # Update focus if this has high attention
        if level >= 0.7:
            self.focus = input_id

        self.attention_history.append((input_id, level))
        return True

    def get_attention(self, input_id: str) -> float:
        """Get current attention to input"""
        return self.attention_weights.get(input_id, 0.0)

    def filter_by_attention(self, inputs: List[SensoryInput], threshold: float = 0.3) -> List[SensoryInput]:
        """Get inputs agent is paying attention to"""
        return [inp for inp in inputs if self.get_attention(inp.input_id) >= threshold]

    def get_attended_features(self, percept: Percept) -> List[PerceptualFeature]:
        """Get features from attended inputs"""
        attended_inputs = {inp.input_id for inp in percept.inputs if self.get_attention(inp.input_id) >= 0.3}
        return [f for f in percept.features if f.source_input in attended_inputs]

    def to_dict(self) -> Dict:
        return {
            "attended_inputs": len(self.attention_weights),
            "current_focus": self.focus if self.focus else "none",
            "history_length": len(self.attention_history)
        }


class SensoryFusion:
    """Combine multiple modalities into unified perception"""

    def __init__(self):
        self.fusion_history: Dict[str, Percept] = {}

    def fuse(self, percept: Percept) -> bool:
        """Fuse multiple sensory inputs into integrated perception"""
        if not percept.inputs:
            return False

        # Calculate integration confidence
        modality_count = len(percept.get_modalities())
        feature_count = len(percept.features)

        # More modalities and features = higher confidence
        percept.understanding_confidence = min(
            1.0,
            (modality_count * 0.2) + (min(feature_count, 10) * 0.08)
        )

        # Create integrated meaning
        if percept.is_multimodal():
            modalities_str = ", ".join(m.value for m in percept.get_modalities())
            percept.integrated_meaning = f"Multi-modal perception: {modalities_str}"
        else:
            modality = percept.get_modalities()[0].value
            percept.integrated_meaning = f"Single modality: {modality}"

        # Calculate emotional response from all inputs
        percept.emotional_response = sum(
            inp.emotional_valence for inp in percept.inputs
        ) / max(1, len(percept.inputs))

        self.fusion_history[percept.percept_id] = percept
        return True

    def get_fused_percept(self, percept_id: str) -> Optional[Percept]:
        """Get fused percept by ID"""
        return self.fusion_history.get(percept_id)

    def to_dict(self) -> Dict:
        return {
            "total_fusions": len(self.fusion_history),
            "multimodal_count": len([p for p in self.fusion_history.values() if p.is_multimodal()]),
            "avg_confidence": round(
                sum(p.understanding_confidence for p in self.fusion_history.values()) /
                max(1, len(self.fusion_history)), 2
            ) if self.fusion_history else 0.0
        }


class PerceptionSystem:
    """Central perception system for agent"""

    def __init__(self):
        self.processors: Dict[ModalityType, ModalityProcessor] = {
            m: ModalityProcessor(m) for m in ModalityType
        }
        self.attention = AttentionMechanism()
        self.fusion = SensoryFusion()
        self.percepts: Dict[str, Percept] = {}

    def perceive(self, sensory_input: SensoryInput) -> Optional[Percept]:
        """Process sensory input"""
        percept = Percept(f"percept_{len(self.percepts)}")
        percept.add_input(sensory_input)

        # Process through modality processor
        processor = self.processors[sensory_input.modality]
        features = processor.process(sensory_input)

        for feature in features:
            percept.add_feature(feature)

        # Apply attention
        self.attention.set_attention(sensory_input.input_id, sensory_input.attention_required)

        # Fuse
        self.fusion.fuse(percept)

        self.percepts[percept.percept_id] = percept
        return percept

    def perceive_multimodal(self, inputs: List[SensoryInput]) -> Optional[Percept]:
        """Process multiple sensory inputs together"""
        percept = Percept(f"percept_{len(self.percepts)}")

        for sensory_input in inputs:
            percept.add_input(sensory_input)
            processor = self.processors[sensory_input.modality]
            features = processor.process(sensory_input)

            for feature in features:
                percept.add_feature(feature)

            self.attention.set_attention(sensory_input.input_id, sensory_input.attention_required)

        self.fusion.fuse(percept)
        self.percepts[percept.percept_id] = percept
        return percept

    def get_attended_perception(self) -> List[Percept]:
        """Get percepts agent is focusing on"""
        return [
            p for p in self.percepts.values()
            if self.attention.get_attention(p.inputs[0].input_id) >= 0.3
        ] if self.percepts else []

    def to_dict(self) -> Dict:
        return {
            "total_percepts": len(self.percepts),
            "attention": self.attention.to_dict(),
            "fusion": self.fusion.to_dict()
        }


# ===== Tests =====

def test_sensory_input_creation():
    """Test creating sensory input"""
    inp = SensoryInput(
        "inp1", ModalityType.TEXT, "Hello world",
        intensity=0.8
    )
    assert inp.input_id == "inp1"
    assert inp.modality == ModalityType.TEXT


def test_perceptual_feature():
    """Test creating perceptual feature"""
    feature = PerceptualFeature(
        "feat1", "sentiment", "inp1",
        0.8, confidence=0.9
    )
    assert feature.feature_id == "feat1"
    assert feature.confidence == 0.9


def test_percept_creation():
    """Test creating percept"""
    percept = Percept("percept1")
    inp = SensoryInput("inp1", ModalityType.TEXT, "test", 0.8)

    assert percept.add_input(inp) is True


def test_percept_multimodal():
    """Test multimodal percept"""
    percept = Percept("percept1")
    percept.add_input(SensoryInput("inp1", ModalityType.TEXT, "test", 0.8))
    percept.add_input(SensoryInput("inp2", ModalityType.VISION, "image", 0.7))

    assert percept.is_multimodal() is True
    assert len(percept.get_modalities()) == 2


def test_modality_processor_text():
    """Test text modality processor"""
    processor = ModalityProcessor(ModalityType.TEXT)
    inp = SensoryInput("inp1", ModalityType.TEXT, "Hello world great", 0.8)

    features = processor.process(inp)
    assert len(features) >= 2  # word count + sentiment


def test_modality_processor_vision():
    """Test vision modality processor"""
    processor = ModalityProcessor(ModalityType.VISION)
    inp = SensoryInput("inp1", ModalityType.VISION, "bright image", 0.9)

    features = processor.process(inp)
    assert len(features) >= 1


def test_attention_mechanism():
    """Test attention mechanism"""
    attention = AttentionMechanism()

    assert attention.set_attention("inp1", 0.8) is True
    assert attention.get_attention("inp1") == 0.8


def test_attention_focus():
    """Test attention focus"""
    attention = AttentionMechanism()

    attention.set_attention("inp1", 0.5)
    attention.set_attention("inp2", 0.8)

    assert attention.focus == "inp2"  # High attention sets focus


def test_attention_filter():
    """Test filtering inputs by attention"""
    attention = AttentionMechanism()

    inputs = [
        SensoryInput("inp1", ModalityType.TEXT, "test1", 0.8),
        SensoryInput("inp2", ModalityType.TEXT, "test2", 0.8),
        SensoryInput("inp3", ModalityType.TEXT, "test3", 0.8),
    ]

    attention.set_attention("inp1", 0.8)
    attention.set_attention("inp2", 0.2)

    filtered = attention.filter_by_attention(inputs, threshold=0.3)
    assert len(filtered) == 1


def test_sensory_fusion():
    """Test sensory fusion"""
    fusion = SensoryFusion()

    percept = Percept("p1")
    percept.add_input(SensoryInput("inp1", ModalityType.TEXT, "test", 0.8))
    percept.add_input(SensoryInput("inp2", ModalityType.VISION, "image", 0.7))
    percept.add_feature(PerceptualFeature("f1", "type1", "inp1", "value"))

    assert fusion.fuse(percept) is True
    assert percept.understanding_confidence > 0.0


def test_perception_system_single_modality():
    """Test perception system with single input"""
    system = PerceptionSystem()

    inp = SensoryInput("inp1", ModalityType.TEXT, "Hello great world", 0.8)
    percept = system.perceive(inp)

    assert percept is not None
    assert len(percept.features) > 0


def test_perception_system_multimodal():
    """Test perception system with multiple inputs"""
    system = PerceptionSystem()

    inputs = [
        SensoryInput("inp1", ModalityType.TEXT, "Hello", 0.8, emotional_valence=0.5),
        SensoryInput("inp2", ModalityType.VISION, "Bright image", 0.9, emotional_valence=0.3),
    ]

    percept = system.perceive_multimodal(inputs)

    assert percept is not None
    assert percept.is_multimodal() is True
    assert abs(percept.emotional_response - 0.4) < 0.01  # Average of 0.5 and 0.3


def test_perception_system_attention():
    """Test attention in perception system"""
    system = PerceptionSystem()

    inp1 = SensoryInput("inp1", ModalityType.TEXT, "Important", 0.8, attention_required=0.9)
    inp2 = SensoryInput("inp2", ModalityType.TEXT, "Ignore", 0.2, attention_required=0.1)

    percept1 = system.perceive(inp1)
    percept2 = system.perceive(inp2)

    attended = system.get_attended_perception()
    assert len(attended) >= 1


def test_complete_perception_workflow():
    """Test complete multimodal perception workflow"""
    system = PerceptionSystem()

    # Perceive multiple modalities with emotional content
    inputs = [
        SensoryInput(
            "inp1", ModalityType.TEXT, "The weather is terrible",
            intensity=0.7, emotional_valence=-0.8, attention_required=0.9
        ),
        SensoryInput(
            "inp2", ModalityType.VISION, "Dark stormy sky",
            intensity=0.9, emotional_valence=-0.7, attention_required=0.8
        ),
        SensoryInput(
            "inp3", ModalityType.AUDIO, "Thunder sound",
            intensity=0.95, emotional_valence=-0.9, attention_required=0.85
        ),
    ]

    percept = system.perceive_multimodal(inputs)

    assert percept is not None
    assert percept.is_multimodal() is True
    assert len(percept.get_modalities()) == 3
    assert percept.understanding_confidence > 0.3
    assert percept.emotional_response < 0.0  # Negative emotion


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
