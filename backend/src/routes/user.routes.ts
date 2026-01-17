import { Router, Response } from 'express';
import { body, validationResult } from 'express-validator';
import { authenticate, AuthRequest } from '../middleware/auth.middleware';
import prisma from '../config/database';

const router = Router();

// Get user profile
router.get('/profile', authenticate, async (req: AuthRequest, res: Response) => {
  try {
    const user = await prisma.user.findUnique({
      where: { id: req.user.id },
      select: {
        id: true,
        email: true,
        name: true,
        profilePicture: true,
        phoneNumber: true,
        address: true,
        dateOfBirth: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ user });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update user profile
router.put(
  '/profile',
  authenticate,
  [
    body('name').optional().trim(),
    body('phoneNumber').optional().trim(),
    body('address').optional().trim(),
    body('dateOfBirth').optional().isISO8601().toDate(),
  ],
  async (req: AuthRequest, res: Response) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      const { name, phoneNumber, address, dateOfBirth } = req.body;

      const updatedUser = await prisma.user.update({
        where: { id: req.user.id },
        data: {
          name: name || undefined,
          phoneNumber: phoneNumber || undefined,
          address: address || undefined,
          dateOfBirth: dateOfBirth || undefined,
        },
        select: {
          id: true,
          email: true,
          name: true,
          profilePicture: true,
          phoneNumber: true,
          address: true,
          dateOfBirth: true,
          updatedAt: true,
        },
      });

      res.json({
        message: 'Profile updated successfully',
        user: updatedUser,
      });
    } catch (error) {
      console.error('Update profile error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);

export default router;
