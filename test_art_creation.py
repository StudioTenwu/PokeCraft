"""
Round 18: Art Creation Integration System

Enable agents to engage in creative expression through music, drawing, 
writing, and other artistic modalities with skill progression and galleries.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional


class ArtModality(Enum):
    """Types of artistic expression"""
    MUSIC = "music"
    DRAWING = "drawing"
    WRITING = "writing"
    DANCE = "dance"
    SCULPTURE = "sculpture"


class CreativeStyle(Enum):
    """Styles of artistic expression"""
    ABSTRACT = "abstract"
    REALISTIC = "realistic"
    SURREAL = "surreal"
    MINIMALIST = "minimalist"
    MAXIMALIST = "maximalist"
    IMPRESSIONIST = "impressionist"


@dataclass
class ArtisticSkill:
    """Represents a skill in an artistic modality"""
    modality: ArtModality
    style: CreativeStyle
    skill_level: float = 0.0  # 0.0-1.0
    pieces_created: int = 0
    hours_practiced: float = 0.0
    critique_average: float = 0.5  # 0.0-1.0

    def practice(self, hours: float = 1.0) -> bool:
        """Practice the artistic skill"""
        self.hours_practiced += hours
        # Learning curve: improvement based on practice
        improvement = min(0.02, (hours / 50.0))
        self.skill_level = min(1.0, self.skill_level + improvement)
        return True

    def create_piece(self) -> bool:
        """Create an artistic piece"""
        self.pieces_created += 1
        return True

    def receive_critique(self, score: float) -> bool:
        """Receive critique (0.0-1.0) and update average"""
        if not (0.0 <= score <= 1.0):
            return False
        # Running average of critiques
        total_score = self.critique_average * max(1, self.pieces_created - 1) + score
        self.critique_average = total_score / self.pieces_created
        return True

    def reach_mastery(self) -> bool:
        """Check if mastery level reached"""
        return self.skill_level >= 0.9 and self.pieces_created >= 10

    def to_dict(self) -> Dict:
        return {
            "modality": self.modality.value,
            "style": self.style.value,
            "skill_level": self.skill_level,
            "pieces_created": self.pieces_created,
            "mastered": self.reach_mastery()
        }


@dataclass
class ArtPiece:
    """An individual artwork"""
    piece_id: str
    title: str
    artist_id: str
    modality: ArtModality
    style: CreativeStyle
    creation_date: float = 0.0
    description: str = ""
    quality_score: float = 0.5
    views: int = 0
    favorites: int = 0

    def view(self) -> bool:
        """Record a view"""
        self.views += 1
        return True

    def favorite(self) -> bool:
        """Record a favorite"""
        self.favorites += 1
        return True

    def get_popularity(self) -> float:
        """Calculate popularity (0.0-1.0)"""
        if self.views == 0:
            return 0.0
        return min(1.0, self.favorites / max(1, self.views))

    def to_dict(self) -> Dict:
        return {
            "piece_id": self.piece_id,
            "title": self.title,
            "artist_id": self.artist_id,
            "modality": self.modality.value,
            "style": self.style.value,
            "quality": self.quality_score,
            "popularity": self.get_popularity()
        }


@dataclass
class ArtGallery:
    """Gallery for displaying artworks"""
    gallery_id: str
    gallery_name: str
    pieces: List[ArtPiece] = field(default_factory=list)
    total_views: int = 0
    creation_date: float = 0.0

    def add_piece(self, piece: ArtPiece) -> bool:
        """Add artwork to gallery"""
        if piece.piece_id in [p.piece_id for p in self.pieces]:
            return False
        self.pieces.append(piece)
        return True

    def remove_piece(self, piece_id: str) -> bool:
        """Remove artwork from gallery"""
        piece = next((p for p in self.pieces if p.piece_id == piece_id), None)
        if piece is None:
            return False
        self.pieces.remove(piece)
        return True

    def get_piece_count(self) -> int:
        """Get number of pieces in gallery"""
        return len(self.pieces)

    def get_gallery_rating(self) -> float:
        """Calculate average quality of all pieces"""
        if not self.pieces:
            return 0.0
        avg_quality = sum(p.quality_score for p in self.pieces) / len(self.pieces)
        return avg_quality

    def to_dict(self) -> Dict:
        return {
            "gallery_id": self.gallery_id,
            "gallery_name": self.gallery_name,
            "piece_count": self.get_piece_count(),
            "gallery_rating": self.get_gallery_rating(),
            "pieces": [p.to_dict() for p in self.pieces]
        }


@dataclass
class CreativeMode:
    """Mode for creative expression"""
    agent_id: str
    available_modalities: List[ArtModality] = field(default_factory=list)
    skills: Dict[ArtModality, ArtisticSkill] = field(default_factory=dict)
    gallery: Optional[ArtGallery] = None
    inspiration_level: float = 0.5  # 0.0-1.0
    creative_energy: float = 1.0  # 0.0-1.0

    def unlock_modality(self, modality: ArtModality) -> bool:
        """Unlock an artistic modality"""
        if modality in self.available_modalities:
            return False
        self.available_modalities.append(modality)
        # Initialize skill for new modality
        self.skills[modality] = ArtisticSkill(modality, CreativeStyle.ABSTRACT)
        return True

    def switch_style(self, modality: ArtModality, style: CreativeStyle) -> bool:
        """Switch artistic style for a modality"""
        if modality not in self.available_modalities:
            return False
        self.skills[modality].style = style
        return True

    def gain_inspiration(self, amount: float = 0.1) -> bool:
        """Gain inspiration for creativity"""
        self.inspiration_level = min(1.0, self.inspiration_level + amount)
        return True

    def use_creative_energy(self, amount: float = 0.1) -> bool:
        """Use creative energy for creating art"""
        if self.creative_energy < amount:
            return False
        self.creative_energy -= amount
        self.creative_energy = max(0.0, self.creative_energy)
        return True

    def recover_energy(self, amount: float = 0.2) -> bool:
        """Recover creative energy through rest"""
        self.creative_energy = min(1.0, self.creative_energy + amount)
        return True

    def create_artwork(self, modality: ArtModality, title: str) -> Optional[ArtPiece]:
        """Create an artwork"""
        if modality not in self.available_modalities:
            return None
        if not self.use_creative_energy(0.2):
            return None
        
        skill = self.skills[modality]
        skill.create_piece()
        
        piece = ArtPiece(
            piece_id=f"{self.agent_id}_{modality.value}_{skill.pieces_created}",
            title=title,
            artist_id=self.agent_id,
            modality=modality,
            style=skill.style,
            quality_score=min(1.0, 0.3 + skill.skill_level * 0.7)
        )
        
        if self.gallery:
            self.gallery.add_piece(piece)
        
        return piece

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "modalities": [m.value for m in self.available_modalities],
            "inspiration_level": self.inspiration_level,
            "creative_energy": self.creative_energy,
            "skills": {m.value: s.to_dict() for m, s in self.skills.items()},
            "gallery": self.gallery.to_dict() if self.gallery else None
        }


class CreativeFramework:
    """Manages creative abilities across agents"""

    def __init__(self):
        self.agents_creative_modes: Dict[str, CreativeMode] = {}
        self.all_artworks: List[ArtPiece] = []
        self.global_gallery: ArtGallery = ArtGallery(
            gallery_id="global",
            gallery_name="Global Art Gallery"
        )

    def enable_creative_mode(self, agent_id: str) -> CreativeMode:
        """Enable creative mode for an agent"""
        if agent_id not in self.agents_creative_modes:
            gallery = ArtGallery(
                gallery_id=f"{agent_id}_gallery",
                gallery_name=f"{agent_id}'s Gallery"
            )
            creative_mode = CreativeMode(
                agent_id=agent_id,
                gallery=gallery
            )
            self.agents_creative_modes[agent_id] = creative_mode
        return self.agents_creative_modes[agent_id]

    def unlock_for_agent(self, agent_id: str, modality: ArtModality) -> bool:
        """Unlock an artistic modality for an agent"""
        mode = self.enable_creative_mode(agent_id)
        return mode.unlock_modality(modality)

    def create_artwork(self, agent_id: str, modality: ArtModality, title: str) -> Optional[ArtPiece]:
        """Create artwork for an agent"""
        mode = self.enable_creative_mode(agent_id)
        piece = mode.create_artwork(modality, title)
        if piece:
            self.all_artworks.append(piece)
            self.global_gallery.add_piece(piece)
        return piece

    def get_agent_portfolio(self, agent_id: str) -> Optional[ArtGallery]:
        """Get agent's personal art gallery"""
        mode = self.agents_creative_modes.get(agent_id)
        if mode:
            return mode.gallery
        return None

    def get_global_gallery(self) -> ArtGallery:
        """Get the global art gallery"""
        return self.global_gallery

    def get_top_artists(self, limit: int = 5) -> List[Dict]:
        """Get top artists by portfolio rating"""
        artist_ratings = []
        for agent_id, mode in self.agents_creative_modes.items():
            if mode.gallery and mode.gallery.get_piece_count() > 0:
                rating = mode.gallery.get_gallery_rating()
                artist_ratings.append({
                    "agent_id": agent_id,
                    "rating": rating,
                    "pieces": mode.gallery.get_piece_count()
                })
        return sorted(artist_ratings, key=lambda x: x["rating"], reverse=True)[:limit]


# ===== Tests =====

def test_artistic_skill_creation():
    """Test creating artistic skill"""
    skill = ArtisticSkill(
        modality=ArtModality.MUSIC,
        style=CreativeStyle.ABSTRACT
    )
    assert skill.modality == ArtModality.MUSIC
    assert skill.skill_level == 0.0


def test_artistic_skill_practice():
    """Test practicing artistic skill"""
    skill = ArtisticSkill(modality=ArtModality.DRAWING, style=CreativeStyle.REALISTIC)
    for _ in range(5):
        skill.practice(hours=10.0)
    assert skill.hours_practiced == 50.0
    assert skill.skill_level > 0.0


def test_artistic_skill_piece_creation():
    """Test creating pieces"""
    skill = ArtisticSkill(modality=ArtModality.WRITING, style=CreativeStyle.SURREAL)
    for _ in range(15):
        skill.create_piece()
    assert skill.pieces_created == 15


def test_artistic_skill_critique():
    """Test receiving critique"""
    skill = ArtisticSkill(modality=ArtModality.MUSIC, style=CreativeStyle.MINIMALIST, critique_average=0.0)
    # First create a piece before critiquing
    skill.create_piece()
    assert skill.receive_critique(0.8) is True
    # With initial critique_average=0.0, should be 0.8
    assert skill.critique_average == 0.8


def test_artistic_skill_mastery():
    """Test reaching mastery"""
    skill = ArtisticSkill(modality=ArtModality.DRAWING, style=CreativeStyle.IMPRESSIONIST)
    skill.skill_level = 0.95
    for _ in range(10):
        skill.create_piece()
    assert skill.reach_mastery() is True


def test_art_piece_creation():
    """Test creating an artwork"""
    piece = ArtPiece(
        piece_id="piece_001",
        title="Moonlight Sonata",
        artist_id="agent_001",
        modality=ArtModality.MUSIC,
        style=CreativeStyle.ABSTRACT,
        quality_score=0.8
    )
    assert piece.title == "Moonlight Sonata"


def test_art_piece_popularity():
    """Test artwork popularity tracking"""
    piece = ArtPiece(
        piece_id="piece_002",
        title="Abstract Forest",
        artist_id="agent_001",
        modality=ArtModality.DRAWING,
        style=CreativeStyle.ABSTRACT,
        quality_score=0.7
    )
    for _ in range(10):
        piece.view()
    for _ in range(3):
        piece.favorite()
    assert piece.get_popularity() == 0.3


def test_art_gallery_creation():
    """Test creating an art gallery"""
    gallery = ArtGallery(
        gallery_id="gallery_001",
        gallery_name="Agent's Gallery"
    )
    assert gallery.gallery_name == "Agent's Gallery"
    assert gallery.get_piece_count() == 0


def test_art_gallery_add_pieces():
    """Test adding pieces to gallery"""
    gallery = ArtGallery(gallery_id="gallery_001", gallery_name="My Gallery")
    for i in range(5):
        piece = ArtPiece(
            piece_id=f"piece_{i:03d}",
            title=f"Work {i}",
            artist_id="agent_001",
            modality=ArtModality.DRAWING,
            style=CreativeStyle.ABSTRACT,
            quality_score=0.6 + i * 0.05
        )
        assert gallery.add_piece(piece) is True
    assert gallery.get_piece_count() == 5


def test_art_gallery_rating():
    """Test calculating gallery rating"""
    gallery = ArtGallery(gallery_id="gallery_001", gallery_name="My Gallery")
    for i in range(3):
        piece = ArtPiece(
            piece_id=f"piece_{i:03d}",
            title=f"Work {i}",
            artist_id="agent_001",
            modality=ArtModality.MUSIC,
            style=CreativeStyle.ABSTRACT,
            quality_score=0.6 + i * 0.05  # 0.6, 0.65, 0.70
        )
        gallery.add_piece(piece)
    # Average of 0.6, 0.65, 0.70 = 0.65
    assert abs(gallery.get_gallery_rating() - 0.65) < 0.01


def test_creative_mode_initialization():
    """Test initializing creative mode"""
    mode = CreativeMode(agent_id="agent_001")
    assert mode.agent_id == "agent_001"
    assert mode.inspiration_level == 0.5


def test_creative_mode_unlock_modality():
    """Test unlocking artistic modalities"""
    mode = CreativeMode(agent_id="agent_001")
    assert mode.unlock_modality(ArtModality.MUSIC) is True
    assert ArtModality.MUSIC in mode.available_modalities
    assert mode.unlock_modality(ArtModality.DRAWING) is True
    assert len(mode.available_modalities) == 2


def test_creative_mode_style_switching():
    """Test switching artistic styles"""
    mode = CreativeMode(agent_id="agent_001")
    mode.unlock_modality(ArtModality.DRAWING)
    assert mode.switch_style(ArtModality.DRAWING, CreativeStyle.REALISTIC) is True
    assert mode.skills[ArtModality.DRAWING].style == CreativeStyle.REALISTIC


def test_creative_energy_management():
    """Test creative energy tracking"""
    mode = CreativeMode(agent_id="agent_001", creative_energy=1.0)
    assert mode.use_creative_energy(0.2) is True
    assert mode.creative_energy == 0.8
    assert mode.recover_energy(0.1) is True
    assert mode.creative_energy == 0.9


def test_create_artwork_workflow():
    """Test creating artwork"""
    mode = CreativeMode(agent_id="agent_001")
    gallery = ArtGallery(gallery_id="personal", gallery_name="My Works")
    mode.gallery = gallery
    
    mode.unlock_modality(ArtModality.MUSIC)
    mode.skills[ArtModality.MUSIC].skill_level = 0.7
    
    piece = mode.create_artwork(ArtModality.MUSIC, "Symphony No. 1")
    assert piece is not None
    assert piece.title == "Symphony No. 1"
    assert gallery.get_piece_count() == 1


def test_creative_framework_agent_enablement():
    """Test enabling creative mode for agents"""
    framework = CreativeFramework()
    mode = framework.enable_creative_mode("agent_001")
    assert mode.agent_id == "agent_001"
    assert "agent_001" in framework.agents_creative_modes


def test_creative_framework_unlock():
    """Test unlocking modalities through framework"""
    framework = CreativeFramework()
    assert framework.unlock_for_agent("agent_001", ArtModality.DRAWING) is True
    mode = framework.enable_creative_mode("agent_001")
    assert ArtModality.DRAWING in mode.available_modalities


def test_creative_framework_create_artwork():
    """Test creating artwork through framework"""
    framework = CreativeFramework()
    framework.unlock_for_agent("agent_001", ArtModality.MUSIC)
    
    piece = framework.create_artwork("agent_001", ArtModality.MUSIC, "Prelude in C")
    assert piece is not None
    assert len(framework.all_artworks) == 1
    assert framework.global_gallery.get_piece_count() == 1


def test_creative_framework_top_artists():
    """Test ranking top artists"""
    framework = CreativeFramework()
    
    # Create artworks for multiple agents
    for agent_num in range(3):
        agent_id = f"agent_{agent_num:03d}"
        framework.unlock_for_agent(agent_id, ArtModality.DRAWING)
        
        for _ in range(5):
            framework.create_artwork(agent_id, ArtModality.DRAWING, f"Artwork {_}")
    
    top_artists = framework.get_top_artists(limit=3)
    assert len(top_artists) == 3
    assert all("agent_id" in artist for artist in top_artists)


def test_complete_artistic_workflow():
    """Test complete artistic workflow"""
    framework = CreativeFramework()
    
    # Agent develops artistic skills
    mode = framework.enable_creative_mode("creative_agent")
    mode.unlock_modality(ArtModality.MUSIC)
    mode.unlock_modality(ArtModality.DRAWING)
    
    # Agent practices and creates
    mode.skills[ArtModality.MUSIC].practice(hours=50.0)
    mode.gain_inspiration(0.2)
    
    for i in range(5):
        piece = framework.create_artwork("creative_agent", ArtModality.MUSIC, f"Composition {i}")
        if piece:
            piece.view()
            piece.favorite()
    
    # Check portfolio
    portfolio = framework.get_agent_portfolio("creative_agent")
    assert portfolio is not None
    assert portfolio.get_piece_count() == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
