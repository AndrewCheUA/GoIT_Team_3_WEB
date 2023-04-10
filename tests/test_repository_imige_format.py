import unittest
from unittest.mock import AsyncMock 
from app.database.models import ImageFormat, User, Image
from app.repository.image_formats import create_image_format
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError



class TestRepositoryImagesFormats(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1)
        self.image = Image(id=1)
        self.body = {
            "width": 0,
            "height": 0,
            "crop": "fill",
            "gravity": "center"
            }
        

    async def test_create_image_format_success(self):
 
        result = await create_image_format(user_id=self.user.id, image_id=self.image.id, format_=self.body, db=self.session)

        self.assertIsInstance(result, ImageFormat)
        self.assertEqual(result.format, self.body)
        self.assertEqual(result.user_id, self.user.id)
        self.assertEqual(result.image_id, self.image.id)
        self.assertTrue(hasattr(result, 'id'))

        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(result)


        
    async def test_create_image_format_failure(self):
        
        self.session.commit.side_effect = IntegrityError(None, None, None)

        result = await create_image_format(user_id=self.user.id, image_id=self.image.id, format_=self.body, db=self.session)

        self.assertIsNone(result)



if __name__ == '__main__':
    unittest.main()
    