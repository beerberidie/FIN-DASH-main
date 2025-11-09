import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCards, deleteCard, Card } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Plus, Loader2, Wallet, ArrowLeft, CreditCard as CreditCardIcon } from 'lucide-react';
import { CardList } from '@/components/CardList';
import { CardCreateDialog } from '@/components/CardCreateDialog';
import { CardEditDialog } from '@/components/CardEditDialog';
import { CardAnalyticsDialog } from '@/components/CardAnalyticsDialog';
import { useToast } from '@/hooks/use-toast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

export default function Cards() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [analyticsDialogOpen, setAnalyticsDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);

  const { data: cards = [], isLoading } = useQuery({
    queryKey: ['cards'],
    queryFn: getCards,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteCard,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cards'] });
      toast({
        title: 'Success',
        description: 'Card deleted successfully',
      });
      setDeleteDialogOpen(false);
      setSelectedCard(null);
    },
    onError: (error: Error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const handleEdit = (card: Card) => {
    setSelectedCard(card);
    setEditDialogOpen(true);
  };

  const handleDelete = (card: Card) => {
    setSelectedCard(card);
    setDeleteDialogOpen(true);
  };

  const handleViewAnalytics = (card: Card) => {
    setSelectedCard(card);
    setAnalyticsDialogOpen(true);
  };

  const confirmDelete = () => {
    if (selectedCard) {
      deleteMutation.mutate(selectedCard.id);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link to="/">
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <div className="p-2 rounded-lg bg-gradient-primary">
                <Wallet className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">FIN-DASH Cards</h1>
                <p className="text-sm text-muted-foreground">Manage your payment cards and track spending</p>
              </div>
            </div>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Card
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-6">

          {/* Cards List */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : (
            <CardList
              cards={cards}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onViewAnalytics={handleViewAnalytics}
            />
          )}
        </div>
      </main>

      {/* Dialogs */}
      <CardCreateDialog open={createDialogOpen} onOpenChange={setCreateDialogOpen} />

      <CardEditDialog
        card={selectedCard}
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
      />

      <CardAnalyticsDialog
        card={selectedCard}
        open={analyticsDialogOpen}
        onOpenChange={setAnalyticsDialogOpen}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the card "{selectedCard?.name}". This action cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-red-600 hover:bg-red-700"
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

